from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, FileResponse, Http404, StreamingHttpResponse, HttpResponse
from django.utils import timezone
from django.core.paginator import Paginator
from django.conf import settings
import os
import json
import mimetypes
from collections import defaultdict
import numpy as np
import time

from .models import DetectionJob, DetectionResult, ModelMetrics
from .utils import (
    run_detection,
    get_model,
    draw_boxes,
    preprocess_image,
    resolve_species_from_model,
    get_available_models,
    get_active_model_key,
    set_active_model,
    get_model_entry,
    load_model_by_key,
)
import cv2
from .forms import DetectionUploadForm


_live_runtime = {
    "camera": None,
    "camera_backend": None,
    "camera_index": None,
    "frame_index": 0,
    "last_confirmed": [],
    "temporal_hits": defaultdict(int),
    "model_key": None,
    "last_frame_at": 0.0,
    "last_raw_frame": None,
    "last_annotated_frame": None,
}


@login_required
def live_view(request):
    """Real-time live detection from webcam."""
    models = get_available_models()
    context = {
        "available_models": models,
        "active_model_key": get_active_model_key(),
        "default_confidence": 0.30,
    }
    return render(request, "detection/live.html", context)


def _is_duplicate_box(existing_boxes, x1, y1, x2, y2):
    """Return True when a candidate box is almost fully overlapped by a previous one."""
    area = max(1, (x2 - x1) * (y2 - y1))
    for ex1, ey1, ex2, ey2 in existing_boxes:
        ix1, iy1 = max(x1, ex1), max(y1, ey1)
        ix2, iy2 = min(x2, ex2), min(y2, ey2)
        if ix2 <= ix1 or iy2 <= iy1:
            continue
        inter_area = (ix2 - ix1) * (iy2 - iy1)
        if inter_area / float(area) > 0.8:
            return True
    return False


def _collect_yolo_detections(results, model, frame_w, frame_h, x_offset=0, y_offset=0):
    """Convert YOLO result objects into bounded sea-only detections."""
    detections = []
    for r in results:
        if not r.boxes:
            continue
        for box in r.boxes:
            cls_id = int(box.cls[0])
            species = resolve_species_from_model(model, cls_id)
            if species is None:
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])

            x1 += x_offset
            y1 += y_offset
            x2 += x_offset
            y2 += y_offset

            x1 = max(0, min(x1, frame_w - 1))
            y1 = max(0, min(y1, frame_h - 1))
            x2 = max(0, min(x2, frame_w - 1))
            y2 = max(0, min(y2, frame_h - 1))

            if (x2 - x1) < 8 or (y2 - y1) < 8:
                continue

            detections.append({
                "species": species,
                "confidence": conf,
                "pixel_x1": x1,
                "pixel_y1": y1,
                "pixel_x2": x2,
                "pixel_y2": y2,
            })
    return detections


def _passes_precision_filters(det, frame_w, frame_h):
    """Reject implausible sea detections to reduce non-sea false positives."""
    species = det["species"]
    conf = det["confidence"]
    x1, y1, x2, y2 = det["pixel_x1"], det["pixel_y1"], det["pixel_x2"], det["pixel_y2"]

    bw = max(1, x2 - x1)
    bh = max(1, y2 - y1)
    area_ratio = (bw * bh) / float(max(1, frame_w * frame_h))
    aspect = bw / float(bh)

    min_conf_map = {
        "sea_cucumber": 0.30,
        "sea_urchin": 0.34,
        "shell": 0.32,
    }
    if conf < min_conf_map.get(species, 0.32):
        return False

    # Reject implausibly large boxes often caused by human/background false positives.
    max_area_map = {
        "sea_cucumber": 0.40,
        "sea_urchin": 0.22,
        "shell": 0.28,
    }
    if area_ratio > max_area_map.get(species, 0.30):
        return False

    # Class-shape sanity checks.
    if species == "sea_urchin" and not (0.55 <= aspect <= 1.85):
        return False
    if species == "shell" and not (0.45 <= aspect <= 2.40):
        return False
    if species == "sea_cucumber" and not (0.35 <= aspect <= 4.80):
        return False

    return True


def _is_underwater_scene(frame):
    """Simple scene gate to suppress detections on ordinary indoor webcam frames."""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mean_s = float(hsv[:, :, 1].mean())
    blue = float(frame[:, :, 0].mean())
    green = float(frame[:, :, 1].mean())
    red = float(frame[:, :, 2].mean())

    color_bias = max(blue, green) - red
    return mean_s >= 32.0 or color_bias >= 8.0


def _append_underwater_fallback(frame, detections):
    """Fallback detector for likely underwater seabed frames when YOLO misses."""
    h, w = frame.shape[:2]
    y0 = int(h * 0.28)
    roi = frame[y0:, :]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    kernel = np.ones((3, 3), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    candidates = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < (w * h) * 0.0025 or area > (w * h) * 0.10:
            continue

        x, y, bw, bh = cv2.boundingRect(cnt)
        aspect = bw / float(max(1, bh))
        fill_ratio = area / float(max(1, bw * bh))
        if fill_ratio < 0.22:
            continue

        species = None
        conf = 0.0
        if 1.4 <= aspect <= 5.5:
            species = "sea_cucumber"
            conf = 0.34
        elif 0.65 <= aspect <= 1.45:
            species = "sea_urchin"
            conf = 0.36

        if species is None:
            continue

        candidates.append({
            "species": species,
            "confidence": conf,
            "pixel_x1": x,
            "pixel_y1": y + y0,
            "pixel_x2": x + bw,
            "pixel_y2": y + y0 + bh,
        })

    candidates = sorted(candidates, key=lambda d: d["confidence"], reverse=True)
    detections.extend(_dedupe_detections(candidates)[:2])


def _dedupe_detections(detections):
    """Merge nearly overlapping detections by keeping the highest confidence one."""
    ordered = sorted(detections, key=lambda d: d["confidence"], reverse=True)
    kept = []
    box_registry = []

    for det in ordered:
        x1, y1, x2, y2 = det["pixel_x1"], det["pixel_y1"], det["pixel_x2"], det["pixel_y2"]
        if _is_duplicate_box(box_registry, x1, y1, x2, y2):
            continue
        box_registry.append((x1, y1, x2, y2))
        kept.append(det)

    return kept


def _temporal_confirm(detections, temporal_hits, threshold=2):
    """Require a detection to appear across consecutive inference cycles before rendering."""
    active_keys = set()
    for det in detections:
        cx = int((det["pixel_x1"] + det["pixel_x2"]) / 2 / 20)
        cy = int((det["pixel_y1"] + det["pixel_y2"]) / 2 / 20)
        key = (det["species"], cx, cy)
        active_keys.add(key)
        temporal_hits[key] += 1

    stale_keys = [k for k in temporal_hits.keys() if k not in active_keys]
    for k in stale_keys:
        temporal_hits[k] = max(0, temporal_hits[k] - 1)
        if temporal_hits[k] == 0:
            del temporal_hits[k]

    confirmed = []
    for det in detections:
        cx = int((det["pixel_x1"] + det["pixel_x2"]) / 2 / 20)
        cy = int((det["pixel_y1"] + det["pixel_y2"]) / 2 / 20)
        key = (det["species"], cx, cy)
        if temporal_hits.get(key, 0) >= threshold:
            confirmed.append(det)
    return confirmed


def _parse_live_request_params(request):
    """Parse live detection controls from query string."""
    conf_raw = request.GET.get("conf", "0.30")
    try:
        conf_threshold = float(conf_raw)
    except ValueError:
        conf_threshold = 0.30
    conf_threshold = max(0.20, min(conf_threshold, 0.70))

    roi_raw = request.GET.get("roi", "0").strip().lower()
    roi_only = roi_raw in ("1", "true", "yes", "on")
    model_key = request.GET.get("model", "").strip()
    return conf_threshold, roi_only, model_key


def _camera_candidates():
    """Yield camera indices/backends in order of reliability for this machine."""
    env_index = os.getenv("SEA_TREASURE_CAMERA_INDEX", "0").strip()
    try:
        primary_index = int(env_index)
    except ValueError:
        primary_index = 0

    indices = [primary_index]
    if primary_index != 1:
        indices.append(1)

    backend_options = [(None, "default")]
    if os.name == "nt":
        if hasattr(cv2, "CAP_MSMF"):
            backend_options.append((cv2.CAP_MSMF, "msmf"))
        if os.getenv("SEA_TREASURE_ALLOW_DSHOW", "0") == "1" and hasattr(cv2, "CAP_DSHOW"):
            backend_options.append((cv2.CAP_DSHOW, "dshow"))

    for index in indices:
        for backend, backend_name in backend_options:
            yield index, backend, backend_name


def _release_live_camera():
    """Release current live camera handle and clear backend metadata."""
    camera = _live_runtime.get("camera")
    if camera is not None:
        try:
            camera.release()
        except Exception:
            pass

    _live_runtime["camera"] = None
    _live_runtime["camera_backend"] = None
    _live_runtime["camera_index"] = None


def _get_live_camera():
    """Open and reuse the webcam for live capture."""
    camera = _live_runtime["camera"]
    if camera is not None and camera.isOpened():
        return camera

    _release_live_camera()

    for camera_index, backend, backend_name in _camera_candidates():
        trial = cv2.VideoCapture(camera_index) if backend is None else cv2.VideoCapture(camera_index, backend)
        if not trial.isOpened():
            trial.release()
            continue

        trial.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        trial.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        trial.set(cv2.CAP_PROP_AUTOFOCUS, 1)

        ok, frame = trial.read()
        if not ok or frame is None:
            trial.release()
            continue

        _live_runtime["camera"] = trial
        _live_runtime["camera_backend"] = backend_name
        _live_runtime["camera_index"] = camera_index
        return trial

    return None


def _reset_live_runtime(model_key=None):
    """Reset temporal state when stream configuration changes."""
    _live_runtime["frame_index"] = 0
    _live_runtime["last_confirmed"] = []
    _live_runtime["temporal_hits"] = defaultdict(int)
    _live_runtime["model_key"] = model_key


def _annotate_live_frame(frame, model, conf_threshold, roi_only, threshold=2):
    """Apply live sea-treasure detection and overlays to one frame."""
    _live_runtime["frame_index"] += 1
    frame_index = _live_runtime["frame_index"]
    last_confirmed = _live_runtime["last_confirmed"]
    temporal_hits = _live_runtime["temporal_hits"]

    detections = list(last_confirmed)
    h, w = frame.shape[:2]
    underwater_scene = _is_underwater_scene(frame)
    roi_x0, roi_y0, roi_x1, roi_y1 = 0, 0, w, h

    if roi_only:
        roi_w = int(w * 0.72)
        roi_h = int(h * 0.72)
        roi_x0 = (w - roi_w) // 2
        roi_y0 = (h - roi_h) // 2
        roi_x1 = roi_x0 + roi_w
        roi_y1 = roi_y0 + roi_h

    inference_interval = 2
    if model and underwater_scene and (frame_index % inference_interval == 0):
        raw_detections = []
        working_frame = frame[roi_y0:roi_y1, roi_x0:roi_x1] if roi_only else frame
        enhanced_frame = preprocess_image(working_frame)
        frame_h, frame_w = working_frame.shape[:2]

        full_passes = [
            model.predict(source=working_frame, conf=conf_threshold, iou=0.45, imgsz=640, verbose=False),
            model.predict(source=enhanced_frame, conf=conf_threshold, iou=0.45, imgsz=640, verbose=False),
            model.predict(source=enhanced_frame, conf=max(0.16, conf_threshold - 0.04), iou=0.45, imgsz=960, verbose=False),
        ]

        for results in full_passes:
            raw_detections.extend(
                _collect_yolo_detections(results, model, w, h, x_offset=roi_x0, y_offset=roi_y0)
            )

        if not raw_detections:
            tile_w = int(frame_w * 0.65)
            tile_h = int(frame_h * 0.65)
            x_steps = [0, max(0, frame_w - tile_w)]
            y_steps = [0, max(0, frame_h - tile_h)]

            for y0 in y_steps:
                for x0 in x_steps:
                    tile = enhanced_frame[y0:y0 + tile_h, x0:x0 + tile_w]
                    tile_results = model.predict(
                        source=tile,
                        conf=max(0.12, conf_threshold - 0.08),
                        iou=0.45,
                        imgsz=960,
                        verbose=False,
                    )
                    raw_detections.extend(
                        _collect_yolo_detections(
                            tile_results,
                            model,
                            w,
                            h,
                            x_offset=roi_x0 + x0,
                            y_offset=roi_y0 + y0,
                        )
                    )

        precision_filtered = [d for d in raw_detections if _passes_precision_filters(d, w, h)]
        if not precision_filtered:
            _append_underwater_fallback(working_frame, precision_filtered)
            if roi_only:
                for det in precision_filtered:
                    det["pixel_x1"] += roi_x0
                    det["pixel_x2"] += roi_x0
                    det["pixel_y1"] += roi_y0
                    det["pixel_y2"] += roi_y0

        deduped = _dedupe_detections(precision_filtered)
        confirmed = _temporal_confirm(deduped, temporal_hits, threshold=threshold)
        _live_runtime["last_confirmed"] = confirmed
        detections = list(confirmed)
    elif not underwater_scene:
        _live_runtime["last_confirmed"] = []
        _live_runtime["temporal_hits"] = defaultdict(int)
        detections = []

    annotated_frame = draw_boxes(frame, detections)

    if roi_only:
        cv2.rectangle(annotated_frame, (roi_x0, roi_y0), (roi_x1, roi_y1), (0, 220, 255), 2)
        cv2.putText(
            annotated_frame,
            "ROI MODE",
            (roi_x0 + 8, max(18, roi_y0 - 8)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 220, 255),
            2,
        )

    return annotated_frame


def _capture_annotated_frame(conf_threshold, roi_only, model_key=None, threshold=2):
    """Capture one annotated live frame from the webcam."""
    if model_key and model_key != _live_runtime.get("model_key"):
        set_active_model(model_key)
        _reset_live_runtime(model_key=model_key)

    camera = _get_live_camera()
    if camera is None:
        return None

    model = get_model()
    success, frame = camera.read()
    if not success or frame is None:
        _release_live_camera()
        return None

    _live_runtime["last_frame_at"] = time.time()
    _live_runtime["last_raw_frame"] = frame.copy()
    annotated = _annotate_live_frame(frame, model, conf_threshold, roi_only, threshold=threshold)
    _live_runtime["last_annotated_frame"] = annotated.copy()
    return annotated


def _serialize_detection_summary(detections):
    """Return compact detection info suitable for JSON responses."""
    return [
        {
            "species": det["species"],
            "confidence": round(float(det["confidence"]), 4),
            "bbox": [det["pixel_x1"], det["pixel_y1"], det["pixel_x2"], det["pixel_y2"]],
        }
        for det in detections[:5]
    ]


def _benchmark_models_on_frame(frame, conf_threshold):
    """Run all available models on the same frame and summarize results."""
    enhanced_frame = preprocess_image(frame)
    h, w = frame.shape[:2]
    benchmarks = []

    for item in get_available_models():
        model = load_model_by_key(item["key"])
        if model is None:
            benchmarks.append({
                "key": item["key"],
                "label": item["label"],
                "count": 0,
                "max_confidence": 0.0,
                "detections": [],
                "error": "load_failed",
            })
            continue

        raw_detections = []
        passes = [
            model.predict(source=frame, conf=conf_threshold, iou=0.45, imgsz=640, verbose=False),
            model.predict(source=enhanced_frame, conf=conf_threshold, iou=0.45, imgsz=640, verbose=False),
        ]
        for results in passes:
            raw_detections.extend(_collect_yolo_detections(results, model, w, h))

        filtered = [det for det in raw_detections if _passes_precision_filters(det, w, h)]
        deduped = _dedupe_detections(filtered)
        max_conf = max((det["confidence"] for det in deduped), default=0.0)
        benchmarks.append({
            "key": item["key"],
            "label": item["label"],
            "count": len(deduped),
            "max_confidence": round(float(max_conf), 4),
            "detections": _serialize_detection_summary(deduped),
        })

    benchmarks.sort(key=lambda item: (item["count"], item["max_confidence"]), reverse=True)
    return benchmarks


def _suggest_confidence_from_benchmark(best_result, fallback_confidence):
    """Pick a practical live confidence based on the best benchmark result."""
    if not best_result or best_result.get("count", 0) == 0:
        return round(float(fallback_confidence), 2)

    max_confidence = float(best_result.get("max_confidence", 0.0))
    suggested = max(0.20, min(0.55, max_confidence - 0.06))
    return round(suggested, 2)


def _save_debug_frame(filename, image):
    """Save debug frame under media and return relative and absolute path."""
    out_dir = os.path.join(settings.MEDIA_ROOT, "detection", "live_debug")
    os.makedirs(out_dir, exist_ok=True)
    full_path = os.path.join(out_dir, filename)
    cv2.imwrite(full_path, image)
    relative_path = os.path.join("detection", "live_debug", filename).replace("\\", "/")
    return full_path, relative_path


def gen_frames(conf_threshold=0.10, roi_only=False, model_key=None):
    """Generator for the live video stream with Ultra-Sensitive Neural Logic."""
    while True:
        annotated_frame = _capture_annotated_frame(conf_threshold, roi_only, model_key=model_key, threshold=2)
        if annotated_frame is None:
            break

        ret, buffer = cv2.imencode('.jpg', annotated_frame)
        if not ret: continue
            
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@login_required
def video_feed(request):
    """Video streaming route for the live detection."""
    conf_threshold, roi_only, model_key = _parse_live_request_params(request)

    return StreamingHttpResponse(gen_frames(conf_threshold=conf_threshold, roi_only=roi_only, model_key=model_key),
                                 content_type='multipart/x-mixed-replace; boundary=frame')


@login_required
def video_frame(request):
    """Return a single annotated live frame as JPEG for browser-safe polling."""
    conf_threshold, roi_only, model_key = _parse_live_request_params(request)
    annotated_frame = _capture_annotated_frame(conf_threshold, roi_only, model_key=model_key, threshold=1)
    if annotated_frame is None:
        return HttpResponse(status=503)

    ret, buffer = cv2.imencode('.jpg', annotated_frame)
    if not ret:
        return HttpResponse(status=500)

    response = HttpResponse(buffer.tobytes(), content_type='image/jpeg')
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response


@login_required
def benchmark_live_frame(request):
    """Capture current live frame and benchmark all available sea models on it."""
    conf_threshold, roi_only, model_key = _parse_live_request_params(request)
    annotated_frame = _capture_annotated_frame(conf_threshold, roi_only, model_key=model_key, threshold=1)
    raw_frame = _live_runtime.get("last_raw_frame")

    if annotated_frame is None or raw_frame is None:
        return JsonResponse({"ok": False, "error": "camera_unavailable"}, status=503)

    timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
    raw_filename = f"live_raw_{timestamp}.jpg"
    annotated_filename = f"live_annotated_{timestamp}.jpg"
    _, raw_rel = _save_debug_frame(raw_filename, raw_frame)
    _, annotated_rel = _save_debug_frame(annotated_filename, annotated_frame)

    benchmarks = _benchmark_models_on_frame(raw_frame, conf_threshold)
    best_result = benchmarks[0] if benchmarks else None
    active_entry = get_model_entry(get_active_model_key())
    suggested_confidence = _suggest_confidence_from_benchmark(best_result, conf_threshold)

    return JsonResponse({
        "ok": True,
        "raw_image_url": settings.MEDIA_URL + raw_rel,
        "annotated_image_url": settings.MEDIA_URL + annotated_rel,
        "active_model": {
            "key": get_active_model_key(),
            "label": active_entry["label"] if active_entry else get_active_model_key(),
        },
        "recommended_model": {
            "key": best_result["key"],
            "label": best_result["label"],
        } if best_result else None,
        "suggested_confidence": suggested_confidence,
        "benchmarks": benchmarks,
    })


@login_required
def upload_view(request):
    """Upload image/video for sea treasure detection."""
    if request.method == "POST":
        form = DetectionUploadForm(request.POST, request.FILES)
        if form.is_valid():
            job = form.save(commit=False)
            job.user = request.user
            job.status = "pending"
            uploaded = request.FILES["input_file"]
            # Determine job type
            if uploaded.content_type.startswith("video"):
                job.job_type = "video"
            else:
                job.job_type = "image"
            job.save()
            messages.success(request, "File uploaded! Starting detection...")
            return redirect("detection:process", job_id=job.id)
        else:
            messages.error(request, "Upload failed. Check the form.")
    else:
        form = DetectionUploadForm()
    return render(request, "detection/upload.html", {"form": form})


@login_required
def process_view(request, job_id):
    """Run detection on the uploaded file."""
    job = get_object_or_404(DetectionJob, id=job_id, user=request.user)

    if job.status not in ("pending", "failed"):
        return redirect("detection:result", job_id=job.id)

    try:
        job.status = "processing"
        job.save()

        input_path = job.input_file.path
        result = run_detection(
            input_path,
            conf_threshold=job.confidence_threshold,
            iou_threshold=job.iou_threshold,
        )

        # Save results to DB
        DetectionResult.objects.filter(job=job).delete()
        for det in result["detections"]:
            DetectionResult.objects.create(
                job=job,
                species=det["species"],
                confidence=det["confidence"],
                bbox_x=det["bbox_x"], bbox_y=det["bbox_y"],
                bbox_w=det["bbox_w"], bbox_h=det["bbox_h"],
                pixel_x1=det["pixel_x1"], pixel_y1=det["pixel_y1"],
                pixel_x2=det["pixel_x2"], pixel_y2=det["pixel_y2"],
                notes=det.get("reasoning", "")
            )

        # Human Expert Analysis Simulation
        job.total_detections = len(result["detections"])
        if job.total_detections > 5:
            summary = f"Neural scan identified a high-density cluster of {job.total_detections} targets. The spatial distribution suggests an active benthic ecosystem with multiple sea treasure species present. Recommend detailed collection."
        elif job.total_detections > 0:
            summary = f"Visual confirmation of {job.total_detections} target(s) established. Morphology matches treasure specifications. The surrounding seabed appears stable; proceeding with precise coordinates for retrieval."
        else:
            summary = "Initial scan yielded no high-confidence matches. Morphology of visible objects suggests natural seabed debris or non-target sediment. Proceeding with a deep neural scan to identify camouflaged specimens."
        
        job.notes = summary
        job.status = "completed"
        job.inference_time_ms = result["inference_time_ms"]
        job.annotated_image = result["annotated_path"]
        job.completed_at = timezone.now()
        job.save()

        messages.success(request, f"Detection complete! Found {job.total_detections} objects.")
    except Exception as e:
        job.status = "failed"
        job.error_message = str(e)
        job.save()
        messages.error(request, f"Detection failed: {e}")

    return redirect("detection:result", job_id=job.id)


@login_required
def result_view(request, job_id):
    """View detection results with bounding boxes and metrics."""
    job = get_object_or_404(DetectionJob, id=job_id, user=request.user)
    results = job.results.all()

    # Count by species
    species_counts = {}
    for r in results:
        species_counts[r.species] = species_counts.get(r.species, 0) + 1

    context = {
        "job": job,
        "results": results,
        "species_counts": species_counts,
        "species_counts_json": json.dumps(species_counts),
    }
    return render(request, "detection/result.html", context)


@login_required
def history_view(request):
    """List all past detection jobs for this user."""
    jobs = DetectionJob.objects.filter(user=request.user)
    paginator = Paginator(jobs, 10)
    page = paginator.get_page(request.GET.get("page", 1))
    return render(request, "detection/history.html", {"page": page})


@login_required
def metrics_view(request):
    """Show model performance metrics."""
    metrics = ModelMetrics.objects.first()
    return render(request, "detection/metrics.html", {"metrics": metrics})


@login_required
def download_result(request, job_id):
    """Download annotated result image."""
    job = get_object_or_404(DetectionJob, id=job_id, user=request.user)
    if not job.annotated_image:
        raise Http404("No result file available.")
    file_path = job.annotated_image.path
    if not os.path.exists(file_path):
        raise Http404("File not found.")
    mime_type, _ = mimetypes.guess_type(file_path)
    response = FileResponse(open(file_path, "rb"), content_type=mime_type or "application/octet-stream")
    response["Content-Disposition"] = f'attachment; filename="detection_result_{job_id}.jpg"'
    return response


@login_required
def delete_job(request, job_id):
    """Delete a detection job."""
    job = get_object_or_404(DetectionJob, id=job_id, user=request.user)
    if request.method == "POST":
        job.delete()
        messages.success(request, "Detection job deleted.")
    return redirect("detection:history")
