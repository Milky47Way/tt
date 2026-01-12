from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from . import models
from django.views.generic import ListView, DetailView, CreateView, View, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import TaskForm, TaskFilterForm, CommentForm
from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .mixins import UserIsOwnerMixin

# Деталі завдання та додавання коментарів
class TaskDetailView(LoginRequiredMixin, DetailView):
    model = models.Task
    context_object_name = "task"
    template_name = 'task/task_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        return context

    def post(self, request, *args, **kwargs):

        comment_form = CommentForm(request.POST, request.FILES)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.author = request.user
            comment.task = self.get_object()
            comment.save()
            return redirect('task:task-detail', pk=comment.task.pk)
        return self.get(request, *args, **kwargs)

# Редагування коментаря (тут можна змінити фото)
class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Comment
    fields = ['content', 'media']
    template_name = 'task/edit_comment.html'

    def form_valid(self, form):
        if self.get_object().author != self.request.user:
            raise PermissionDenied
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('task:task-detail', kwargs={'pk': self.object.task.pk})


class CommentLikeToggle(LoginRequiredMixin, View):
    def post(self, request, pk):
        comment = get_object_or_404(models.Comment, pk=pk)
        like, created = models.Like.objects.get_or_create(comment=comment, user=request.user)
        if not created:
            like.delete()
        return HttpResponseRedirect(comment.get_absolute_url())