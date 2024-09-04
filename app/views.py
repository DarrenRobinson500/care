from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from .forms import *
from datetime import *

def home(request):
    if not request.user.is_authenticated:
        return redirect("login")

    staff, model, form, nav_models, colour = get_info(request, None)
    if staff.user_type == "Staff": return redirect('ind', 'staff', staff.id)

    system_description = [
        "Fully scalable to the number of users and data volumes",
        "Access on laptops and phones",
        "Full AWS Security",
        "User/Staff Registration"
        "Multiple levels of access"
        "Patient information",
        "Staff information",
        "Rostering",
        "Job management - including SMS prompts",
        "One off and recurring jobs"
        "Invoicing and Data to Finance",
        "Medication information incorporated into Job creation",
        "Notes",
    ]

    complete = [
        "User System",
        "Ability to switch between user types easily for testing",
        "Workload",
        "Roster system - view of upcoming work vs staff",
        "Financials to accounts",
        "Medication",
        "Incidents",
        "Info Model",
        "Text messages",
        "Look and Feel",
        "Uploads",
        "Downloads",
        "Logo",
        "Upload Information fields",
        "Pictures",
        "Multi colour",
    ]

    to_do = [
        "Environment variables",
        "Git",
        "Amazon",
        "Checking input files",
        "Testing",
    ]

    context = {"to_do": to_do, 'complete': complete, 'system_description': system_description, 'nav_models': nav_models, 'staff': staff, 'colour': colour}
    return render(request, 'home.html', context)

# --------------------------------
# ------ Authentication ----------
# --------------------------------

def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        if form.is_valid():
            user = form.save()
            user.first_name = firstname
            user.last_name = lastname
            user.save()
            Staff(name=firstname+" "+lastname, user=user, user_type="Staff").save()
            login(request, user)
            return redirect("home")
    else:
        form = UserCreationForm()
    context = {'form': form, 'colour': colours[0]}
    return render(request, 'registration/signup.html', context)

def switch_user(request, user_type):
    if user_type == "setup": username = "local"
    if user_type == "admin": username = "Matt"
    if user_type == "staff": username = "Allison"
    password = "FoxyRoxy1997"
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
    return redirect("home")

def custom_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        print("Login", username, password)
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")  # Redirect to your desired page after login
        else:
            print("Log in error")
            messages.success(request, ("There was an error logging you in."))
            # Handle invalid login
    else:
        form = AuthenticationForm()
    context = {'form': form, 'colour': colours[0]}
    return render(request, "registration/login.html", context)

def custom_logout(request):
    logout(request)
    return redirect("custom_login")

# ----------------------------
# ------ Utilities  ----------
# ----------------------------

def get_info(request, model_str, id=None):
    staff = Staff.objects.filter(user=request.user).first()
    # print("Get Info Colour 1:", staff.id, colours[staff.colour_no])

    if not request.user.is_authenticated: return redirect("login")
    staff, current_model, current_form, nav_models = None, None, None, None
    for model in models:
        if model.model_str == model_str: current_model = model
    for form in forms:
        if form._meta.model.model_str == model_str: current_form = form
    # print("Get info model:", model, current_model == Info)
    if current_model == Info and id:
        item = model.objects.get(id=id)
        # print("Get info item:", item)
        if item.info_field.data_type == "text": current_form = InfoTextForm
        if item.info_field.data_type == "date": current_form = InfoDateForm
        if item.info_field.data_type == "number": current_form = InfoNumberForm
    # print("Get info", model_str, current_model, current_form)
    staff = Staff.objects.filter(user=request.user).first()
    # print("Get Info Colour:", staff.id, colours[staff.colour_no])
    if staff.user_type == "Staff": nav_models = [nav_models_staff, None]
    if staff.user_type == "Admin": nav_models = [nav_models_admin, None]
    if staff.user_type == "Setup": nav_models = [nav_models_admin, nav_models_setup]
    colour = staff.colour()
    return staff, current_model, current_form, nav_models, colour

def get_model(model_str):
    for model in models:
        if model.model_str == model_str: return model

def get_form(model_str):
    for form in forms:
        # print("Get form:", form, form._meta.model.model_str, model_str)
        if form._meta.model.model_str == model_str: return form

def get_staff(request):
    staff = Staff.objects.filter(user=request.user).first()
    return staff

def max_order(model_str):
    model = get_model(model_str)
    items = model.objects.all()
    max_order = 0
    for i in items:
        if i.order and i.order > max_order: max_order = i.order
    return max_order

def make_days(no_of_days):
    today = datetime.today()
    for day_offset in range(no_of_days):
        day = today + timedelta(days=day_offset)
        existing = Day.objects.filter(day=day).first()
        if not existing:
            new = Day(day=day)
            new.save()

def make_months(no_of_months):
    today = datetime.today()
    for month_offset in range(no_of_months):
        month = today.month + month_offset
        year = today.year
        while month > 12:
            month = month - 12
            year = year + 1
        existing = Month.objects.filter(month=month, year=year).first()
        if not existing:
            new = Month(month=month, year=year)
            new.save()

def create_info_items(info_field):
    model = info_field.parent_model()
    items = model.objects.all()
    info_category = info_field.category
    for item in items:
        if info_field.database == "patient": existing = Info.objects.filter(patient=item, info_category=info_category, info_field=info_field)
        if info_field.database == "staff": existing = Info.objects.filter(staff=item, info_category=info_category, info_field=info_field)
        if info_field.database == "recurring_job": existing = Info.objects.filter(recurring_job=item, info_category=info_category, info_field=info_field)
        if info_field.database == "job": existing = Info.objects.filter(job=item, info_category=info_category, info_field=info_field)
        if info_field.database == "month": existing = Info.objects.filter(month=item, info_category=info_category, info_field=info_field)
        if not existing:
            new_info = Info(category=info_field.category, field=info_field.field, order_category=info_category.order, order_field=info_field.order, info_category=info_category, info_field=info_field)
            if info_field.database == "patient": new_info.patient = item
            if info_field.database == "staff": new_info.staff = item
            if info_field.database == "recurring_job": new_info.recurring_job = item
            if info_field.database == "job": new_info.job = item
            if info_field.database == "month": new_info.month = item
            new_info.save()

# ------------------------------------
# ------ Generic Functions  ----------
# ------------------------------------

def list(request, model_str):
    staff, model, form, nav_models, colour = get_info(request, model_str)
    if staff.user_type == "Staff" and model_str == "staff": return redirect('ind', 'staff', staff.id)
    items = model.objects.all()
    if model.has_order: items = items.order_by('order')
    if model == Shift:
        print("Shift items:", items)
        for item in items:
            if not item.start or not item.end: item.save_start_and_end()
            items = model.objects.all()
    if model == Day:
        make_days(14)
        items = items.filter(day__gte=datetime.today(), day__lte=datetime.today() + timedelta(days=15))
    if model == Month: make_months(6)
    if model == File: items = items.order_by('-time_stamp')

    context = {'items': items, 'model': model, 'nav_models': nav_models, 'colour': colour, 'staff': staff}
    if model == Job:
        context['items_unallocated'] = items.filter(staff__isnull=True, date_time_completed__isnull=True)
        context['items_open'] = items.filter(staff__isnull=False, date_time_completed__isnull=True)
        context['items_complete'] = items.filter(date_time_completed__isnull=False)
        context['upcoming_jobs'] = (0, "Today", get_upcoming_jobs(0)), (1, "Tomorrow", get_upcoming_jobs(1))
    # print("List context:", context)
    return render(request, f"{model_str}s.html", context)

def ind(request, model_str, id):
    staff = Staff.objects.get(id=3)
    # print("Ind Colour 1:", staff.id, staff.colour_no, colours[staff.colour_no])

    staff, model, form, nav_models, colour = get_info(request, model_str)
    # print("Ind Colour:", staff.id, colours[staff.colour_no])
    model = get_model(model_str)
    item = model.objects.get(id=id)
    context = {'item': item, 'model': model, 'nav_models': nav_models, 'colour': colour, 'staff': staff}
    return render(request, f"{model_str}.html", context)

def new(request, model_str):
    staff, model, form, nav_models, colour = get_info(request, model_str)
    print("New form:", form)
    if request.method == 'POST':
        form = form(request.POST or None)
        if form.is_valid():
            new_item = form.save()
            if model.has_order:
                new_item.order = max_order(model_str) + 1
                new_item.save()
            if model == Shift: new_item.save_start_and_end()
            if model == InfoField: create_info_items(new_item)
            return redirect('list', model_str)
    mode = "New"
    context = {'form': form, 'model': model, 'nav_models': nav_models, 'mode': mode, 'colour': colour}
    return render(request, f"form.html", context)

def edit(request, model_str, id):
    staff, model, form, nav_models, colour = get_info(request, model_str)
    item = model.objects.get(id=id)
    if request.method == 'POST':
        form = form(request.POST, request.FILES, instance=item)
        if form.is_valid():
            new_item = form.save()
            if model in [Info] and item.info_field.field == "Mobile":
                item.parent().mobile = new_item.content_text
                item.parent().save()
                print("Saved mobile:", new_item.content_text)
            if model in [Note, Info] and new_item.parent(): return redirect('ind', new_item.parent_model_str(), new_item.parent().id)
            return redirect('list', model_str)
    form = form(instance=item)
    mode = "Edit"
    context = {'form': form, 'model': model, 'nav_models': nav_models, 'mode': mode, 'item': item, 'colour': colour}
    return render(request, f"form.html", context)

def delete(request, model_str, id):
    staff, model, form, nav_models, colour = get_info(request, model_str)
    item = model.objects.get(id=id)
    if model_str == "answer":
        item.answer = None
        item.save()
    else:
        item.delete()
    return redirect('list', model_str)

def order(request, model_str, dir, id):
    staff, model, form, nav_models, colour = get_info(request, model_str)
    dir = int(dir)
    item = model.objects.get(id=id)
    items = model.objects.all()
    if not item.order:
        max_order = 1
        for i in items:
            if i.order and i.order > max_order: max_order = i.order
        item.order = max_order + 1
        item.save()
    else:
        swap_item = model.objects.filter(order=item.order+dir).first()
        item.order = item.order + dir
        item.save()
        if swap_item:
            swap_item.order = item.order - dir
            swap_item.save()

    return redirect('list', model_str)

def active(request, model_str, id):
    staff, model, form, nav_models, colour = get_info(request, model_str)
    item = model.objects.get(id=id)
    item.active = not item.active
    item.save()
    return redirect('list', model_str)

def add_note(request, model_str, id):
    staff, model, form, nav_models, colour = get_info(request, model_str)
    item = model.objects.get(id=id)
    form = NoteForm
    if request.method == 'POST':
        form = form(request.POST or None)
        if form.is_valid():
            new_item = form.save()
            if model == Patient: new_item.patient = item
            if model == Staff: new_item.staff = item
            if model == RecurringJob: new_item.recurring_job = item
            if model == Job: new_item.job = item
            if model == Month: new_item.month = item
            new_item.created_by = staff
            new_item.date_time_created = datetime.today()
            new_item.save()
            return redirect('ind', model_str, item.id)
    mode = "New"
    context = {'form': form, 'model': model, 'nav_models': nav_models, 'mode': mode, 'colour': colour}
    return render(request, f"form.html", context)

def action(request, action_type, return_to, model_str, id):
    staff, model, form, nav_models, colour = get_info(request, model_str)
    item = model.objects.get(id=id)
    if action_type == "complete":
        if not item.date_time_completed:
            item.date_time_completed = datetime.now()
            item.amount = item.jobtype.amount
        else:
            item.date_time_completed = None
            item.amount = None
    if action_type == "increment_colour":
        item.colour_no += 1
        if item.colour_no >= len(colours): item.colour_no = 0
        item.save()

    item.save()
    # print("Action Colour:", staff.id, staff.colour_no, colours[staff.colour_no])
    if return_to == "staff":
        if item == staff:
            # print("Action Colour 2:", staff.id, staff.colour_no, colours[staff.colour_no])
            return redirect('ind', 'staff', item.id)
        if item.staff:
            return redirect('ind', 'staff', item.staff.id)
        else:
            print("No item.staff", item.id)
    return redirect('list', model_str)

# ------------------------------------
# ------ Specific Functions ----------
# ------------------------------------

def add_upcoming_jobs(request, day_adj):
    day_adj = int(day_adj)
    requested_day = datetime.now() + timedelta(days=day_adj)
    upcoming_jobs = get_upcoming_jobs(day_adj)
    for recurring_job in upcoming_jobs:
        start = datetime.combine(requested_day.date(), recurring_job.jobtype.start)
        end = datetime.combine(requested_day.date(), recurring_job.jobtype.end)
        Job(jobtype=recurring_job.jobtype, patient=recurring_job.patient, date_time_requested=requested_day,
            start=start, end=end).save()
    return redirect('list', 'job')

def get_upcoming_jobs(day_adj):
    requested_day = datetime.now() + timedelta(days=day_adj)
    day_of_week = requested_day.strftime("%A")
    recurring_jobs = RecurringJob.objects.all()
    new_jobs = []
    for recurring_job in recurring_jobs:
        if recurring_job.frequency == day_of_week or recurring_job.frequency.name == "Every day":
            already_exists = False
            existing = Job.objects.filter(jobtype=recurring_job.jobtype, patient=recurring_job.patient)
            for item in existing:
                if item.date_time_requested.date() == requested_day.date(): already_exists = True
            if not already_exists: new_jobs.append(recurring_job)
    return new_jobs

def add_patient_job(request, patient_id, jobtype_id):
    patient = Patient.objects.get(id=patient_id)
    jobtype = JobType.objects.get(id=jobtype_id)
    frequency = Frequency.objects.get(name="Every day")
    RecurringJob(patient=patient, jobtype=jobtype, frequency=frequency).save()
    return redirect('ind', 'patient', patient_id)

def allocate_job(request, job_id, staff_id):
    job = Job.objects.get(id=job_id)
    staff = Staff.objects.get(id=staff_id)
    job.staff = staff
    job.save()
    return redirect('list', 'job')

def add_shift(request, day_adj, shift_id, staff_id):
    day = datetime.now().date() + timedelta(days=int(day_adj))
    staff = Staff.objects.get(id=staff_id)
    shift = AvailableShift.objects.get(id=shift_id)
    new = Shift(staff=staff, shift=shift, date=day)
    new.save()
    new.save_start_and_end()
    return redirect('ind', 'staff', staff_id)

def create_financial_spreadsheet(request, month_id):
    month = Month.objects.get(id=int(month_id))
    wb = month.create_financial_spreadsheet()
    filename = f"patient_financials_{month.month}_{month.year}.xlsx"
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename={filename}'

    # Save the workbook to the response
    wb.save(response)
    return response
    # return redirect('ind', 'month', int(month_id))

def test_sms(request, model_str, id):
    staff, model, form, nav_models, colour = get_info(request, model_str)
    item = model.objects.get(id=id)

    new_item = None
    if item.parent_model() == Staff: new_item = SMS(staff=item.parent(), content="Test Message", sender=staff)
    if item.parent_model() == Patient: new_item = SMS(patient=item.parent(), content="Test Message", sender=staff)
    if new_item:
        print("Saving and sending")
        new_item.save()
        new_item.send()
    return redirect('ind', item.parent_model_str(), item.parent().id)

def sms_job(request, model_str, id):
    staff, model, form, nav_models, colour = get_info(request, model_str)
    job = model.objects.get(id=id)

    new_item = None
    content = f"Dear {job.staff.user.first_name}, please note a job alert: {job.jobtype} for {job.patient}."
    new_item = SMS(staff=job.staff, patient=job.patient, content=content, sender=staff)
    new_item.save()
    new_item.send()
    return redirect('list', 'job')


# ---------------------------
# ---- File Management ------
# ---------------------------

def file_upload(request, model_str):
    staff, model, form, nav_models, colour = get_info(request, model_str)
    if request.method == "POST":
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            new_file = form.save()
            new_file.save()
            print("Saved File:", new_file, )
            return redirect("list", "file")
    else:
        form = FileForm()
    context = {'form': form, 'model': model, 'nav_models': nav_models, 'colour': colour}
    return render(request, "file_upload.html", context)

def df_to_db_patient(df, model):
    for index, row in df.iterrows():
        if not model.objects.filter(name=row['name']).exists():
            model(name=row['name'], order=max_order(model.model_str) + 1).save()

def df_to_db_infocategory(df, model):
    for index, row in df.iterrows():
        if not model.objects.filter(category=row['category']).exists():
            model(category=row['category'], order=max_order(model.model_str) + 1).save()

def df_to_db_infofield(df, model):
    for index, row in df.iterrows():
        if not model.objects.filter(field=row['field']).exists():
            category = InfoCategory.objects.filter(category=row['category']).first()
            if not category:
                category = InfoCategory(category=row['category'], order=max_order(model.model_str) + 1)
                category.save()
            model(database=row['database'], category=category, field=row['field'], data_type=row['data_type'], order=max_order(model.model_str) + 1).save()

def category_names(id): return InfoCategory.objects.get(id=id).category

def file_to_db(request, model_str, id):
    staff, model, form, nav_models, colour = get_info(request, model_str)
    model = get_model(model_str)
    item = model.objects.get(id=id)
    # Get the dataframe
    df = pd.read_excel(item.document)
    # Add the df to the db
    model = get_model(item.type)
    if item.type == "patient": df_to_db_patient(df, model)
    if item.type == "infocategory": df_to_db_infocategory(df, model)
    if item.type == "infofield": df_to_db_infofield(df, model)
    # Convert the db to HTML
    db = pd.DataFrame.from_records(model.objects.all().values())
    if item.type == "infofield":
        db['category_id'] = db['category_id'].map(category_names)

    db_html = db.to_html(classes=['table', 'table-striped', 'table-center'], index=True, justify='left')
    # Convert the spreadsheet to HTML
    spreadsheet = item.html()
    context = {'form': form, 'model': model, 'nav_models': nav_models, 'spreadsheet': spreadsheet, 'db_html': db_html, 'colour': colour}
    return render(request, "file_to_db.html", context)