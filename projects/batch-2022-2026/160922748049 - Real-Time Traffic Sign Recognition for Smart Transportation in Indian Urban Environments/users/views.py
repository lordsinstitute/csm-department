from django.shortcuts import render, redirect
from .forms import UserProfileForm
from .models import UserProfile
from django.contrib import messages
import csv
import os


def home(request):
    return render(request, 'home.html')


def user_profile_create(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.save()
            messages.success(request, 'User profile created successfully!')
            return redirect('user_profile_create')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserProfileForm()
    
    return render(request, 'register.html', {'form': form})



def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username, password)
        try:
            user = UserProfile.objects.get(username=username)
            print(user.password, user.status)
            if user.password==password and user.status == 'active':
                return render(request, 'users/userhome.html')
            else:
                messages.error(request, 'Need to wait for approval.')
                return render(request, 'userlogin.html')
        except UserProfile.DoesNotExist:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'userlogin.html')

def user_home(request):
    return render(request, 'users/userhome.html')


import os
import csv
from django.conf import settings
from django.shortcuts import render

def metrics_view(request):
    metrics = {}
    image_files = []

    # Path to results.csv (can remain outside static if you prefer)
    metrics_csv_path = os.path.join(settings.BASE_DIR, 'users', 'yolo_project', 'exp1', 'results.csv')

    # Read metrics
    if os.path.exists(metrics_csv_path):
        with open(metrics_csv_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            if rows:
                last_row = rows[-1]
                metrics = {
                    'precision': last_row.get('metrics/precision(B)'),
                    'recall': last_row.get('metrics/recall(B)'),
                    'map': last_row.get('metrics/mAP50(B)') or last_row.get('map50')
                }
            else:
                metrics = {'error': 'Metrics data is empty.'}
    else:
        metrics = {'error': 'Training not completed or metrics file not found.'}

    # # Path to image folder (must be inside static/)
    # image_dir = os.path.join(settings.BASE_DIR, 'users', 'static')
    # if os.path.exists(image_dir):
    #     for file in os.listdir(image_dir):
    #         if file.lower().endswith(('.png', '.jpg', '.jpeg')):
    #             image_files.append(f'yolo_project/exp1/{file}')  # static-relative path

    return render(request, 'users/metrics.html', {
        'metrics': metrics,
        # 'images': image_files
    })


from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from .forms import UploadFileForm
from users.yolo_predict import YOLOPredictor
import os
from django.conf import settings
from PIL import Image
import cv2

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
            output_dir = os.path.join(settings.MEDIA_ROOT, 'outputs')
            os.makedirs(upload_dir, exist_ok=True)
            os.makedirs(output_dir, exist_ok=True)

            fs = FileSystemStorage(location=upload_dir)
            filename = fs.save(uploaded_file.name, uploaded_file)
            file_path = os.path.join(upload_dir, filename)
            output_filename = f'output_{filename}'
            output_path = os.path.join(output_dir, output_filename)

            # Initialize YOLO predictor
            model_path = 'best.pt'
            predictor = YOLOPredictor(model_path)

            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                # Process image
                result_image = predictor.predict_image(file_path)

                # Convert BGR to RGB for PIL compatibility
                result_rgb = cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB)
                Image.fromarray(result_rgb).save(output_path)

                output_url = f'/media/outputs/{output_filename}'
                return render(request, 'users/predict.html', {
                    'output_url': output_url,
                    'is_image': True
                })

            elif filename.lower().endswith(('.mp4', '.avi')):
                # Process video
                predictor.predict_video(file_path, display=False, save_output=True, output_path=output_path)

                output_url = f'/media/outputs/{output_filename}'
                return render(request, 'users/predict.html', {
                    'output_url': output_url,
                    'is_image': False
                })

    else:
        form = UploadFileForm()

    return render(request, 'users/upload.html', {'form': form})

# detector/views.py
from django.http import StreamingHttpResponse
from .yolo_predict import YOLOPredictor
import cv2

predictor = YOLOPredictor('best.pt')

def gen_frames():
    cap = cv2.VideoCapture(0)  # 0 for default webcam

    while True:
        success, frame = cap.read()
        if not success:
            break

        # Run detection and plot results
        result_frame = predictor.predict_frame(frame)

        # Encode to JPEG for streaming
        ret, buffer = cv2.imencode('.jpg', result_frame)
        frame = buffer.tobytes()

        # Yield frame in MJPEG format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

def live_feed(request):
    return StreamingHttpResponse(gen_frames(), content_type='multipart/x-mixed-replace; boundary=frame')

def live_view(request):
    return render(request, 'users/live.html')

