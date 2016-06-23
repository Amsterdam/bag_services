from django.views import generic

from . import models


class JobListView(generic.ListView):
    model = models.JobExecution
    ordering = "-date_started"
    paginate_by = 20


class JobDetailView(generic.DetailView):
    model = models.JobExecution
