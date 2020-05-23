

from .models import AuditForm, AuditSession, AuditQuestion, Audit_Score
from .forms import AuditQuestionFormSet, AuditCreateForm, AuditScoreForm, AuditQuestionForm, CreateSessionForm, \
    SessionNoteForm
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.shortcuts import render, get_object_or_404, redirect
from django.forms.models import inlineformset_factory

from django.urls import reverse_lazy
from django.db import transaction
from .filter import AuditFormFilter, AuditSessionFilter

from utils.decorators import auditor_ad_required_cbv, auditor_ad_required_fbv


class AuditFormListView(ListView):
    model = AuditForm
    template_name = 'audit/form/list.html'

    def get_context_data(self, **kwargs):
        context = super(AuditFormListView, self).get_context_data(**kwargs)
        context['filter'] = AuditFormFilter(self.request.GET)

        return context

    def get_queryset(self):
        qs = self.model.objects.all()
        filtered_list = AuditFormFilter(self.request.GET, queryset=qs)

        return filtered_list.qs

    @auditor_ad_required_cbv
    def dispatch(self, *args, **kwargs):
        return super(AuditFormListView, self).dispatch(*args, **kwargs)


class AuditFormCreate(CreateView):
    model = AuditForm
    template_name = 'audit/form/create.html'
    form_class = AuditCreateForm
    success_url = None

    def get_context_data(self, **kwargs):
        data = super(AuditFormCreate, self).get_context_data(**kwargs)
        if self.request.POST:
            data['question'] = AuditQuestionFormSet(self.request.POST)
        else:
            data['question'] = AuditQuestionFormSet()

        return data

    def form_valid(self, form):
        context = self.get_context_data()
        question = context['question']
        with transaction.atomic():
            form.instance.created_by = self.request.user
            self.object = form.save()
            if question.is_valid():
                question.instance = self.object
                question.save()
        return super(AuditFormCreate, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('audit_form:detail', kwargs={'pk': self.object.pk})

    @auditor_ad_required_cbv
    def dispatch(self, *args, **kwargs):
        return super(AuditFormCreate, self).dispatch(*args, **kwargs)


class AuditFormDetailView(DetailView):
    model = AuditForm
    template_name = "audit/form/detail.html"

    def get_context_data(self, **kwargs):
        data = super(AuditFormDetailView, self).get_context_data(**kwargs)

        data['note_form'] = SessionNoteForm()

        return data

    @auditor_ad_required_cbv
    def dispatch(self, *args, **kwargs):
        return super(AuditFormDetailView, self).dispatch(*args, **kwargs)


@auditor_ad_required_fbv
def form_delete_view(request, pk):
    if request.method == "POST":
        obj = get_object_or_404(AuditForm, pk=pk)
        obj.delete()
    return redirect('audit_form:list')


class AuditFormUpdateView(UpdateView):
    model = AuditForm
    form_class = AuditCreateForm
    template_name = "audit/form/update.html"
    success_url = None

    def get_context_data(self, **kwargs):
        data = super(AuditFormUpdateView, self).get_context_data(**kwargs)

        update_questions_formset = inlineformset_factory(
            AuditForm, AuditQuestion, form=AuditQuestionForm,
            fields=['question'], extra=1, can_delete=True
        )

        if self.request.POST:
            data['question'] = update_questions_formset(self.request.POST, instance=self.object)
        else:
            data['question'] = update_questions_formset(instance=self.object)

        return data

    def form_valid(self, form):
        context = self.get_context_data()
        question = context['question']
        with transaction.atomic():
            if question.is_valid():
                question.instance = self.object
                question.save()
        return super(AuditFormUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('audit_form:detail', kwargs={'pk': self.object.pk})

    @auditor_ad_required_cbv
    def dispatch(self, *args, **kwargs):
        return super(AuditFormUpdateView, self).dispatch(*args, **kwargs)


class AuditSessionListView(ListView):
    model = AuditSession
    template_name = 'audit/session/list.html'

    def get_context_data(self, **kwargs):
        context = super(AuditSessionListView, self).get_context_data(**kwargs)
        context['filter'] = AuditSessionFilter(self.request.GET)

        return context

    def get_queryset(self):
        qs = self.model.objects.all()
        filtered_list = AuditSessionFilter(self.request.GET, queryset=qs)

        return filtered_list.qs

    @auditor_ad_required_cbv
    def dispatch(self, *args, **kwargs):
        return super(AuditSessionListView, self).dispatch(*args, **kwargs)


class AuditSessionDetailView(DetailView):
    model = AuditSession
    template_name = 'audit/session/detail.html'

    #
    def get_context_data(self, **kwargs):
        context = super(AuditSessionDetailView, self).get_context_data(**kwargs)
        context['edit_note_form'] = SessionNoteForm()

        return context

    @auditor_ad_required_cbv
    def dispatch(self, *args, **kwargs):
        return super(AuditSessionDetailView, self).dispatch(*args, **kwargs)


@auditor_ad_required_fbv
def session_note_update(request, session_id):
    session_obj = AuditSession.objects.get(id=session_id)
    if request.method == 'POST':
        form = SessionNoteForm(request.POST)
        if form.is_valid():
            session_obj.note = form.cleaned_data.get('note')
            session_obj.save()

    return redirect('audit_session:detail', pk=session_id)


@auditor_ad_required_fbv
def audit_score_update(request, session_id):
    session_obj = AuditSession.objects.get(id=session_id)
    audit_score_formset = inlineformset_factory(AuditSession, Audit_Score, form=AuditScoreForm, extra=0,
                                                can_delete=False)
    if request.method == 'POST':
        formset = audit_score_formset(request.POST, instance=session_obj)
        if formset.is_valid():
            formset.save()
            return redirect('audit_session:detail', pk=session_id)
    else:
        formset = audit_score_formset(instance=session_obj)

    template_name = 'audit/session/score_update.html'
    context = {
        'formset': formset,
        'object': session_obj,

    }
    return render(request, template_name, context)


@auditor_ad_required_fbv
def session_create_view(request):
    form = CreateSessionForm(request.POST or None)
    if form.is_valid():
        title = form.cleaned_data.get('title')
        branch = form.cleaned_data.get('branch')
        audit_form = form.cleaned_data.get('audit_form')
        auditor = request.user

        new_session = AuditSession.objects.create(title=title, branch=branch, audit_form=audit_form, auditor=auditor)
        audit_score_objs = []
        for question in new_session.audit_form.questions.all():
            new_audit_score_obj = Audit_Score(session=new_session, question=question)
            audit_score_objs.append(new_audit_score_obj)
        Audit_Score.objects.bulk_create(audit_score_objs)
        return redirect('audit_session:list')

    template_name = 'audit/session/create.html'
    context = {'form': form}
    return render(request, template_name, context)


@auditor_ad_required_fbv
def session_delete_view(request, pk):
    if request.method == "POST":
        obj = get_object_or_404(AuditSession, pk=pk)
        obj.delete()
    return redirect('audit_session:list')


@auditor_ad_required_fbv
def session_mark_done(request, pk):
    if request.method == "POST":
        obj = get_object_or_404(AuditSession, pk=pk)
        obj.status = 'done'
        obj.save()
    return redirect('audit_session:detail', pk=pk)


@auditor_ad_required_fbv
def get_report(request, session_id):
    session = AuditSession.objects.get(id=session_id)

    template_name = 'audit/session/report.html'
    context = {
        "object": session,

    }

    return render(request, template_name, context)

