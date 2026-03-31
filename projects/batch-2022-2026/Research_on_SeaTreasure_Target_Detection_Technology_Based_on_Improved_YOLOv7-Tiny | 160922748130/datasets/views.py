from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Dataset
from .forms import DatasetForm


def is_admin(user):
    try:
        return user.profile.role == "admin"
    except Exception:
        return user.is_superuser


@login_required
def dataset_list(request):
    datasets = Dataset.objects.all()
    return render(request, "datasets/list.html", {"datasets": datasets})


@login_required
def dataset_detail(request, pk):
    dataset = get_object_or_404(Dataset, pk=pk)
    return render(request, "datasets/detail.html", {"dataset": dataset})


@login_required
def dataset_upload(request):
    if not is_admin(request.user):
        messages.error(request, "Admin access required.")
        return redirect("datasets:list")
    if request.method == "POST":
        form = DatasetForm(request.POST, request.FILES)
        if form.is_valid():
            ds = form.save(commit=False)
            ds.uploaded_by = request.user
            ds.save()
            messages.success(request, f"Dataset '{ds.name}' uploaded successfully!")
            return redirect("datasets:detail", pk=ds.pk)
    else:
        form = DatasetForm()
    return render(request, "datasets/upload.html", {"form": form})


@login_required
def dataset_delete(request, pk):
    if not is_admin(request.user):
        messages.error(request, "Admin access required.")
        return redirect("datasets:list")
    dataset = get_object_or_404(Dataset, pk=pk)
    if request.method == "POST":
        dataset.delete()
        messages.success(request, "Dataset deleted.")
    return redirect("datasets:list")
