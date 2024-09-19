from datetime import *

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.core.paginator import Paginator

from .forms import *

def home(request):
    if not request.user.is_authenticated:
        return redirect("custom_login")

    links = [(Patient, "#C2F1C8"), (Job, "#C2F1C8"), (Staff, "#C2F1C8"), (RecurringJob, "#FFFFFF"), (Day, "#FFFFFF"), (Month, "#FFFFFF")]

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
        "One off and recurring jobs",
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
        "Environment variables",
        "Git",
    ]

    to_do = [
        "Validate",
        "Publish on-line",
        "Regression testing",
        "User Perspectives x5",
        "Check point [User validated, tested app]",
    ]

    to_do_extra = [
        "Patient -> Recurring Jobs not requested -> Shows calls (but shouldn't)",
        "Automate the addition of recurring jobs to the jobs list",
        "Validate",
        "Amazon",
        "Checking input files",
        "Testing",
        "User Perspectives x5"
    ]

    context = {"links": links, "to_do": to_do, 'complete': complete, 'system_description': system_description, 'nav_models': nav_models, 'staff': staff, 'colour': colour}
    return render(request, 'home.html', context)

# --------------------------------
# ------ Authentication ----------
# --------------------------------

def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        if form.is_valid():
            user = form.save()
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            staff = Staff.objects.filter(first_name=first_name, last_name=last_name).first()
            if staff and staff.user is None:
                print("Found Staff Record")
                staff.user = user
            else:
                print("Created Staff Record")
                staff = Staff(name=first_name+" "+last_name, first_name=first_name, last_name=last_name, user=user, user_type="Staff", colour_no=0)
            staff.save()

            login(request, user)
            return redirect("home")
    else:
        form = UserCreationForm()
    context = {'form': form, 'colour': colours[0]}
    return render(request, 'registration/signup.html', context)

def switch_user(request, user_type):
    print("Switch user:", user_type)
    if user_type == "setup": username = "local"
    if user_type == "admin":
        print("Changing to Matt")
        username = "matt_hollinger"
    if user_type == "staff": username = "Allison_Harpur"
    password = os.environ.get("user_password")
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
    if not request.user.is_authenticated: return redirect("login")
    staff, current_model, current_form, nav_models = None, None, None, None
    for model in models:
        if model.model_str == model_str: current_model = model
    for form in forms:
        if form._meta.model.model_str == model_str: current_form = form
    if current_model == Info and id:
        item = model.objects.get(id=id)
        print("Get info item:", item, item.info_field.data_type)
        if item.info_field.data_type == "text": current_form = InfoTextForm
        if item.info_field.data_type == "text_area": current_form = InfoTextAreaForm
        if item.info_field.data_type == "date": current_form = InfoDateForm
        if item.info_field.data_type == "number": current_form = InfoNumberForm

    staff = Staff.objects.filter(user=request.user).first()
    # print("Get info:", staff, request.user.is_staff)
    if not staff and request.user.is_staff: # If the user is authenticated but doesn't have a Staff instance
        print("Created new staff")
        staff = Staff(user=request.user, user_type="Setup", colour_no=0)
        staff.save()

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
        # existing.initiate()
        if not existing:
            new = Day(day=day)
            new.initiate()
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
        for item in items:
            if not item.start or not item.end: item.save_start_and_end()
        items = model.objects.all()
    if model == Day:
        make_days(14)
        items = items.filter(day__gte=datetime.today(), day__lte=datetime.today() + timedelta(days=15))
        for item in items:
            item.initiate()
    if model == Month: make_months(6)
    if model == File: items = items.order_by('-time_stamp')
    if model == MedicationType: items = items.order_by('category')

    context = {'items': items, 'model': model, 'nav_models': nav_models, 'colour': colour, 'staff': staff}
    if model == Job:
        context['items_unallocated'] = items.filter(staff__isnull=True, date_time_completed__isnull=True)
        context['items_open'] = items.filter(staff__isnull=False, date_time_completed__isnull=True)
        context['items_complete'] = items.filter(date_time_completed__isnull=False)
        context['upcoming_jobs'] = (0, "Today", get_upcoming_jobs(0)), (1, "Tomorrow", get_upcoming_jobs(1))

    if model == Patient:
        p = Paginator(items, 30)
        page = request.GET.get('page')
        context['items'] = p.get_page(page)

    # print("List context:", context)
    return render(request, f"{model_str}s.html", context)

def list_original(request, model_str):
    staff, model, form, nav_models, colour = get_info(request, model_str)
    if staff.user_type == "Staff" and model_str == "staff": return redirect('ind', 'staff', staff.id)
    items = model.objects.all()
    if model.has_order: items = items.order_by('order')
    if model == Shift:
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
    staff, model, form, nav_models, colour = get_info(request, model_str)
    model = get_model(model_str)
    item = model.objects.get(id=id)
    if model in [Patient, Staff]: item.update_links()
    context = {'item': item, 'model': model, 'nav_models': nav_models, 'colour': colour, 'staff': staff}
    return render(request, f"{model_str}.html", context)

def new(request, model_str, id=None, return_to=None):
    staff, model, form, nav_models, colour = get_info(request, model_str)
    print("New form:", form)
    if request.method == 'POST':
        form = form(request.POST, request.FILES)
        if form.is_valid():
            new_item = form.save()
            if model.has_order:
                new_item.order = max_order(model_str) + 1
                new_item.save()
            if model == Shift: new_item.save_start_and_end()
            if model == InfoField: create_info_items(new_item)
            if model == Medication:
                new_item.initiate(id)
                if return_to == "patient": return redirect('ind', 'patient', id)
            return redirect('list', model_str)
    mode = "New"
    context = {'form': form, 'model': model, 'nav_models': nav_models, 'mode': mode, 'colour': colour}
    return render(request, f"form.html", context)

def edit(request, model_str, id, return_to=None):
    staff, model, form, nav_models, colour = get_info(request, model_str, id)
    print("Edit", form, model_str, return_to, return_to == "patient")
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
            if return_to == "patient":
                if model == Patient:
                    return redirect('ind', 'patient', item.id)
                return redirect('ind', 'patient', item.patient.id)
            if return_to == "staff": return redirect('ind', 'staff', item.staff.id)
            return redirect('list', model_str)
    form = form(instance=item)
    mode = "Edit"
    context = {'form': form, 'model': model, 'nav_models': nav_models, 'mode': mode, 'item': item, 'colour': colour}
    return render(request, f"form.html", context)

def delete(request, model_str, id):
    staff, model, form, nav_models, colour = get_info(request, model_str)
    item = model.objects.get(id=id)
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
        if model == InfoField: item.update_infos()
    else:
        swap_item = model.objects.filter(order=item.order+dir).first()
        item.order = item.order + dir
        item.save()
        if model == InfoField:
            print("Updating infos")
            item.update_infos()
        if swap_item:
            swap_item.order = item.order - dir
            swap_item.save()
            if model == InfoField: swap_item.update_infos()

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
    item_staff = None
    if action_type == "delete":
        print("Item to delete:", item)
        item_staff = item.staff
        item_staff = item.staff
        item.delete()
    if action_type == "complete":
        if not item.date_time_completed:
            item.date_time_completed = datetime.now()
            item.amount = item.jobtype.amount
        else:
            item.date_time_completed = None
            item.amount = None
        item.save()
    if action_type == "increment_colour":
        item.colour_no += 1
        if item.colour_no >= len(colours): item.colour_no = 0
        item.save()

    if return_to == "staff":
        if item_staff:
            return redirect('ind', 'staff', item_staff.id)
        if item == staff:
            return redirect('ind', 'staff', item.id)
        if item.staff:
            return redirect('ind', 'staff', item.staff.id)
        else:
            print("No item.staff", item.id)
    if return_to == "job": return redirect('ind', 'job', item.id)
    return redirect('list', model_str)

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
        if not model.objects.filter(field=row['field'], database=row['database']).exists():
            category = InfoCategory.objects.filter(category=row['category']).first()
            if not category:
                category = InfoCategory(category=row['category'], order=max_order(model.model_str) + 1)
                category.save()
            model(database=row['database'], category=category, field=row['field'], data_type=row['data_type'], order=max_order(model.model_str) + 1).save()

def df_to_db_jobtype(df, model):
    for index, row in df.iterrows():
        if not model.objects.filter(name=row['name']).exists():
            start = str(row['start'])
            end = str(row['end'])
            try:
                model(name=row['name'], amount=row['amount'], recurring=row['recurring'], duration=row['duration'],
                      start=start, end=end, order=max_order(model.model_str) + 1).save()
            except:
                model(name=row['name'], amount=row['amount'], recurring=row['recurring'], duration=row['duration'],
                      order=max_order(model.model_str) + 1).save()

def df_to_db_frequency(df, model):
    for index, row in df.iterrows():
        if not model.objects.filter(name=row['name']).exists():
            model(name=row['name'], sunday=row['sunday'], monday=row['monday'], tuesday=row['tuesday'],
                  wednesday=row['wednesday'], thursday=row['thursday'], friday=row['friday'], saturday=row['saturday'],
                  per_day=row['per_day'],
                  order=max_order(model.model_str) + 1).save()

def df_to_db_medicationtype(df, model):
    for index, row in df.iterrows():
        if not model.objects.filter(name=row['name']).exists():
            model(name=row['name'], category=row['category'], order=max_order(model.model_str) + 1).save()

def df_to_db_availableshift(df, model):
    print("Available Shift")
    for index, row in df.iterrows():
        available_shift = model.objects.filter(start=row['start'], end=row['end']).first()
        if not available_shift:
            model(start=row['start'], end=row['end'], active=True, order=max_order(model.model_str) + 1).save()
        else:
            available_shift.start = row['start']
            available_shift.end = row['end']
            available_shift.active = True
            available_shift.save()

def df_to_db_staff(df, model):
    for index, row in df.iterrows():
        staff = model.objects.filter(first_name=row['first_name'], last_name=row['last_name']).first()
        name = row['first_name'] + " " + row['last_name']
        if not staff:
            staff = model(name=name, first_name=row['first_name'], last_name=row['last_name'], user_type=row['user_type'], order=max_order(model.model_str) + 1)
        else:
            staff.name = name
            staff.user_type = row['user_type']
        staff.save()
        has_mobile = False
        try:
            mobile = "0" + str(int(row['mobile']))
            has_mobile = True
        except:
            pass
        if has_mobile:
            info_field = InfoField(field="Mobile")
            info = Info.objects.filter(staff=staff, info_field=info_field).first()
            if info:
                info.content_text = mobile
                info.save()
            staff.mobile = mobile
            staff.save()


def category_names(id): return InfoCategory.objects.get(id=id).category

functions = [("patient", df_to_db_patient), ("staff", df_to_db_staff), ("availableshift", df_to_db_availableshift), ("infocategory", df_to_db_infocategory), ("infofield", df_to_db_infofield),
             ("medicationtype", df_to_db_medicationtype), ("jobtype", df_to_db_jobtype), ('frequency', df_to_db_frequency)]

def file_to_db(request, model_str, id):
    staff, model, form, nav_models, colour = get_info(request, model_str)
    model = get_model(model_str)
    item = model.objects.get(id=id)
    # Get the dataframe
    df = pd.read_excel(item.document)
    # Add the df to the db
    model = get_model(item.type)
    for model_str, function in functions:
        if item.type == model_str: function(df, model)

    # Convert the db to HTML
    try:
        db = pd.DataFrame.from_records(model.objects.all().values())
        if item.type == "infofield": db['category_id'] = db['category_id'].map(category_names)
        db_html = db.to_html(classes=['table', 'table-striped', 'table-center'], index=True, justify='left')
    except:
        db_html = None

    # Convert the spreadsheet to HTML
    spreadsheet = item.html()
    context = {'item': item, 'form': form, 'model': model, 'nav_models': nav_models, 'spreadsheet': spreadsheet, 'db_html': db_html, 'colour': colour}
    return render(request, "file_to_db.html", context)

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
            start=start, end=end, amount=recurring_job.jobtype.amount).save()
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
    new_item = RecurringJob(patient=patient, jobtype=jobtype, frequency=frequency)
    # new_item.save()
    new_item.save_initial()
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

def add_preferred_shift(request, day, shift_id, staff_id):
    staff = Staff.objects.get(id=staff_id)
    available_shift = AvailableShift.objects.get(id=shift_id)
    item = PreferredShift.objects.get(staff=staff, available_shift=available_shift)
    if day == "sunday": item.sunday = not item.sunday
    if day == "monday": item.monday = not item.monday
    if day == "tuesday": item.tuesday = not item.tuesday
    if day == "wednesday": item.wednesday = not item.wednesday
    if day == "thursday": item.thursday = not item.thursday
    if day == "friday": item.friday = not item.friday
    if day == "saturday": item.saturday = not item.saturday
    item.save()
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


def search(request):
    staff, model, form, nav_models, colour = get_info(request, None)
    searched = None
    context = {'nav_models': nav_models, 'colour': colour}
    if request.method == "POST":
        searched = request.POST['searched']
        context['searched'] = searched
        context['patients'] = Patient.objects.filter(name__contains=searched).order_by('name')
        context['staff'] = Staff.objects.filter(name__contains=searched).order_by('name')
        # context = {'searched': searched, 'patients':patients, 'staff': staff, 'nav_models': nav_models, 'colour': colour}
    return render(request, "search.html", context)

def ind_info(request, model_str, id):
    staff, model, form, nav_models, colour = get_info(request, model_str)
    model = get_model(model_str)
    item = model.objects.get(id=id)
    if request.method == 'POST':
        for info in item.info():
            content = request.POST.get(info.field)
            if content != "":
                print("Post info:", info.field, content)
                info.save_content(content)
    context = {'item': item, 'model': model, 'nav_models': nav_models, 'colour': colour, 'staff': staff}
    return render(request, f"{model_str}_info.html", context)

def job_notes(request, model_str, id):
    staff, model, form, nav_models, colour = get_info(request, model_str)
    model = get_model(model_str)
    item = model.objects.get(id=id)
    if request.method == 'POST':
        print("Job notes:", request.POST.get("notes"))
        item.notes = request.POST.get("notes")
        item.save()
    return redirect('ind', 'job', id)