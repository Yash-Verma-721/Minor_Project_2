from django.shortcuts import render,redirect
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.db.models import F, Sum
from  . import models

import time

def landing(request):
    return render(request, 'core/landing.html')

def contact(request):
    return render(request,"core/contact.html")


def home(request):
    return render(request, 'core/home.html')

def logout(request):
    request.session.flush()
    return redirect("/")


@never_cache
def userhome(request):
    if "sunm" not in request.session:
        messages.error(request, "You logged out your account, please login again.")
        return redirect("/login/")

    user_email = request.session["sunm"]

    # user ke notes
    notes = models.ShareNotes.objects.filter(owner=user_email)

    total_files = notes.count()
    shared_files = notes.filter(is_shared=True).count()

    recent_files = notes.order_by("-id")[:5]

    # Storage quota info
    user_obj = models.Signup.objects.filter(email=user_email).first()
    
    if user_obj:
        actual_used = models.ShareNotes.objects.filter(
            owner=user_email
        ).aggregate(total=Sum('file_size'))['total'] or 0
        if user_obj.storage_used != actual_used:
            models.Signup.objects.filter(email=user_email).update(storage_used=actual_used)
            user_obj.storage_used = actual_used

    storage_used  = user_obj.storage_used  if user_obj else 0
    storage_limit = user_obj.storage_limit if user_obj else 300 * 1024 * 1024
    storage_used_mb  = round(storage_used  / (1024 * 1024), 1)
    storage_limit_mb = round(storage_limit / (1024 * 1024), 1)
    storage_pct = min(100, round((storage_used / storage_limit) * 100)) if storage_limit else 0

    context = {
        "sname": request.session.get("sname"),
        "sunm": user_email,
        "total_files": total_files,
        "shared_files": shared_files,
        "recent_files": recent_files,
        "storage_used_mb":  storage_used_mb,
        "storage_limit_mb": storage_limit_mb,
        "storage_pct":      storage_pct,
    }

    return render(request, "core/userhome.html", context)







from .utils import send_verification_mail
import uuid




def signup(request):
    if request.method=="GET":
        return render(request,"core/signup.html",{"output":""})
    else:
        #to recieve data from UI 'form'
        username=request.POST.get("username")
        email=request.POST.get("email")
        password=request.POST.get("password")
        mobile_no=request.POST.get("mobile_no")
        

        #to insert record in database using models
        p=models.Signup(name=username,email=email,password=password,mobile=mobile_no,status=0,role="user",info=time.asctime())
        p.save()

        #to integrate EmailAPI 
        

        send_verification_mail(email, username)

        return render(request,"core/signup.html",{"output":"User register successfully.... Please wait for admin approval or check your email to verify account"})  

def verify(request):
    vemail=request.GET.get("vemail")
    print(f"DEBUG: Verify email={vemail}")
    
    updated = models.Signup.objects.filter(email=vemail).update(status=1)
    print(f"DEBUG: Records updated={updated}")

    return render(request,"core/signup.html",{"output":"Account verified successfully.... "})  


@never_cache  
def user_login(request):
    if request.method=="GET":   
        return render(request,"core/login.html",{"output":""})
      
   
    else:
        email=request.POST.get("email")
        password=request.POST.get("password")
        
        print(f"DEBUG: Email={email}, Password={password}")

        userDetails=models.Signup.objects.filter(email=email,password=password,status=1)
        print(f"DEBUG: Found {len(userDetails)} users")
        
        if len(userDetails)>0:
            print(f"DEBUG: User role = {userDetails[0].role}")
            request.session['sunm']=userDetails[0].email
            request.session['sname']=userDetails[0].name
            request.session['srole']=userDetails[0].role
            
            # Clear any previous messages
            if 'output' in request.session:
                del request.session['output']

            if userDetails[0].role=="admin":
                return redirect("/myadmin/")
            else:    
                return redirect("/userhome/")
        else:
            return render(request,"core/login.html",{"output":"Invalid user or verify your account...."}) 



from django.core.files.base import ContentFile
from .utils import generate_key, encrypt_data

FILE_SIZE_LIMIT    = 30  * 1024 * 1024   # 30 MB per file


@never_cache
def sharenotes(request):

    if "sunm" not in request.session:
        messages.error(request, "You logged out your account, please login again.")
        return redirect("/login/")

    user_email = request.session["sunm"]

    def _get_storage_context(user_obj):
        """Return storage display values for the template."""
        if user_obj:
            actual_used = models.ShareNotes.objects.filter(
                owner=user_obj.email
            ).aggregate(total=Sum('file_size'))['total'] or 0
            if user_obj.storage_used != actual_used:
                models.Signup.objects.filter(email=user_obj.email).update(storage_used=actual_used)
                user_obj.storage_used = actual_used

        used  = user_obj.storage_used  if user_obj else 0
        limit = user_obj.storage_limit if user_obj else 300 * 1024 * 1024
        return {
            "storage_used_mb":  round(used  / (1024 * 1024), 1),
            "storage_limit_mb": round(limit / (1024 * 1024), 1),
            "storage_pct":      min(100, round((used / limit) * 100)) if limit else 0,
        }

    user_obj = models.Signup.objects.filter(email=user_email).first()

    if request.method == "GET":
        ctx = {"sname": request.session.get("sname")}
        ctx.update(_get_storage_context(user_obj))
        return render(request, "core/sharenotes.html", ctx)

    title       = request.POST.get("title")
    category    = request.POST.get("category")
    description = request.POST.get("description")
    uploaded_file = request.FILES["file"]

    # ── Quota Checks ─────────────────────────────────────────────────────────
    base_ctx = {"sname": request.session["sname"]}
    base_ctx.update(_get_storage_context(user_obj))

    if uploaded_file.size > FILE_SIZE_LIMIT:
        base_ctx["error"] = "File too large. Maximum allowed size is 30 MB."
        return render(request, "core/sharenotes.html", base_ctx)

    if user_obj and (user_obj.storage_used + uploaded_file.size) > user_obj.storage_limit:
        base_ctx["error"] = "Storage limit exceeded. You have used all your 300 MB quota."
        return render(request, "core/sharenotes.html", base_ctx)

    # ── Encrypt & Save (unchanged logic) ─────────────────────────────────────
    file_data = uploaded_file.read()
    key = generate_key()
    encrypted_data = encrypt_data(file_data, key)

    original_size = uploaded_file.size  # store before reading changes pointer

    note = models.ShareNotes(
        title=title,
        category=category,
        description=description,
        owner=user_email,
        encryption_key=key.decode(),
        original_filename=uploaded_file.name,
        file_size=original_size,
    )
    # ✅ save encrypted file to MEDIA
    note.file.save(uploaded_file.name, ContentFile(encrypted_data))
    note.save()

    # ── Increment storage_used ────────────────────────────────────────────────
    if user_obj:
        models.Signup.objects.filter(email=user_email).update(
            storage_used=user_obj.storage_used + original_size
        )

    success_ctx = {"sname": request.session["sname"], "output": "Upload Successful!"}
    # Refresh user_obj to get updated storage_used
    user_obj = models.Signup.objects.filter(email=user_email).first()
    success_ctx.update(_get_storage_context(user_obj))
    return render(request, "core/sharenotes.html", success_ctx)

@never_cache
def viewnotes(request):
    
    if "sunm" not in request.session:
        messages.error(request, "You logged out your account, please login again.")
        return redirect("/login/")

    notes = models.ShareNotes.objects.filter(
        owner=request.session["sunm"]
    )

    return render(
        request,
        "core/viewnotes.html",
        {
            "notes": notes,
            "sname": request.session.get("sname")
        }
    )

@never_cache
def generate_link(request, id):

    if "sunm" not in request.session:
      messages.error(request, "You logged out your account, please login again.")       
      return redirect("/login/")

    note = models.ShareNotes.objects.get(
        id=id,
        owner=request.session["sunm"]
    )

    note.is_shared = True
    note.save()

    link = request.build_absolute_uri(
        f"/shared/{note.share_token}"
    )

    notes = models.ShareNotes.objects.filter(
    owner=request.session["sunm"]
)

    return render(
        request,
        "core/viewnotes.html",
        {
        "notes": notes,
        "link": link,
        "sname": request.session["sname"]
        }
)


@never_cache
def cpuser(request):
    #because only logged in user can change password, so we will check session for email, if not found then we will redirect to login page.
    # and the never_cache the session is expierd after the logout, so user can not access cpuser page after logout by using browser back button.
    if "sunm" not in request.session:
        messages.error(request, "You logged out your account, please login again.")
        return redirect("/login/")
    
    email=request.session["sunm"]
    name=request.session["sname"]
    if request.method=="GET":
        return render(request,"core/cpuser.html",{"sname":name,"output":""})
    else:
        opassword=request.POST.get("opassword")
        npassword=request.POST.get("npassword")
        cnpassword=request.POST.get("cnpassword")        

        userDetails=models.Signup.objects.filter(email=email,password=opassword)
        if len(userDetails)>0:
            if npassword==cnpassword:
                models.Signup.objects.filter(email=email).update(password=cnpassword)
                msg="Password changed successfully...."        
            else:
                msg="New & Confirm new password mismatch...."             
        else:
            msg="Invalid old password , please try again...."    
        return render(request,"core/cpuser.html",{"sname":name,"output":msg})
    

from django.shortcuts import get_object_or_404

@never_cache
def delete_note(request, id):

    if "sunm" not in request.session:
        messages.error(request, "You logged out your account, please login again.")
        return redirect("/login/")

    user_email = request.session["sunm"]

    note = get_object_or_404(
        models.ShareNotes,
        id=id,
        owner=user_email,
    )

    # ── Decrement storage_used before deletion ────────────────────────────────
    file_size = note.file_size  # use stored original size

    # delete physical encrypted file
    if note.file:
        note.file.delete()

    # delete database record
    note.delete()

    # Update storage quota (clamp at 0 to avoid negatives)
    user_obj = models.Signup.objects.filter(email=user_email).first()
    if user_obj and file_size > 0:
        new_used = max(0, user_obj.storage_used - file_size)
        models.Signup.objects.filter(email=user_email).update(storage_used=new_used)

    return render(request, "core/viewnotes.html", {
        "notes": models.ShareNotes.objects.filter(owner=user_email),
        "sname": request.session.get("sname"),
        "output": "Note deleted successfully..."
    })

@never_cache
def adminhome(request):

    if "sunm" not in request.session:
        messages.error(request, "You logged out your account, please login again.")
        return redirect("/login/")
    
    return render(request,"core/adminhome.html",{"sname":request.session["sname"]})

@never_cache
def manageusers(request):

    if "sunm" not in request.session:
        messages.error(request, "You logged out your account, please login again.")
        return redirect("/login/")
    
    userDetails=models.Signup.objects.filter(role="user")
    output = ""
    if request.GET.get("status") == "updated":
        output = "User status updated successfully...."
    return render(request,"core/manageusers.html",{"userDetails":userDetails,"sname":request.session["sname"],"output":output})    

@never_cache
def manageuserstatus(request):

    if "sunm" not in request.session:
        messages.error(request, "You logged out your account, please login again.")
        return redirect("/login/")
    
    s=request.GET.get("s")
    regid=int(request.GET.get("regid"))

    if s=="active":
        models.Signup.objects.filter(regid=regid).update(status=1)
    elif s=="inactive":
        models.Signup.objects.filter(regid=regid).update(status=0)
    else:
        models.Signup.objects.filter(regid=regid).delete()

    return redirect("/manageusers/?status=updated")

@never_cache
def cpadmin(request):

    if "sunm" not in request.session:
        messages.error(request, "You logged out your account, please login again.")
        return redirect("/login/")
    
    email=request.session["sunm"]
    if request.method=="GET":
        return render(request,"core/cpadmin.html",{"sname":request.session["sname"],"output":""})
    else:
        # getting data from UI
        opassword=request.POST.get("opassword")
        npassword=request.POST.get("npassword")
        cnpassword=request.POST.get("cnpassword")  

        # userDetails me value tab hi aayegi jab user ki session email or dala hu opassword Sginup module ke parametrs se match hoga. 
        #kyuki agar user galat opassword enter krta hai hai to filter() use model se koi record nhai milega or userDetails empty rhega.
        userDetails=models.Signup.objects.filter(email=email,password=opassword)
        if len(userDetails)>0:
            if npassword==cnpassword:
                models.Signup.objects.filter(email=email).update(password=cnpassword)
                msg="Password changed successfully...."        
            else:
                msg="New & Confirm new password mismatch...."             
        else:
            msg="Invalid old password , please try again...."    
        return render(request,"core/cpadmin.html",{"sname":request.session["sname"],"output":msg})

    
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from tempfile import NamedTemporaryFile
import mimetypes
from .utils import decrypt_data



@never_cache
def shared_file(request, token):

    note = get_object_or_404(
        models.ShareNotes,
        share_token=token
    )

    return render(request, "core/download_page.html", {
        "token": token,
        "filename": note.original_filename
    })


@never_cache
def download_file(request, token):

    note = get_object_or_404(
        models.ShareNotes,
        share_token=token
    )

    # read encrypted file
    with note.file.open("rb") as f:
        encrypted_data = f.read()

    decrypted = decrypt_data(
        encrypted_data,
        note.encryption_key.encode()
    )

    filename = note.original_filename

    content_type, _ = mimetypes.guess_type(filename)

    temp_file = NamedTemporaryFile(delete=True)
    temp_file.write(decrypted)
    temp_file.seek(0)

    return FileResponse(
        temp_file,
        as_attachment=True,
        filename=filename,
        content_type=content_type or "application/octet-stream"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Secure Token-Based File Sharing  
# ─────────────────────────────────────────────────────────────────────────────

import json
from .models import SharedLink
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.db.models import F  # Sum already imported at top


@never_cache
@require_POST
def create_shared_link(request, file_id):
    """
    POST /share/<file_id>/
    Owner-only: creates a SharedLink and returns shareable URL + metadata as JSON.
    """
    if "sunm" not in request.session:
        return JsonResponse({"error": "Authentication required"}, status=401)

    note = get_object_or_404(
        models.ShareNotes,
        id=file_id,
        owner=request.session["sunm"],   # only owner may share
    )

    # Parse optional overrides from request body
    try:
        body = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        body = {}

    expires_hours = int(body.get("expires_hours", 24))
    max_downloads = int(body.get("max_downloads", 5))

    link = SharedLink.objects.create(
        file=note,
        max_downloads=max_downloads,
    )
    # Honour custom expiry after creation so default() isn't stale
    if expires_hours != 24:
        link.expires_at = timezone.now() + __import__("datetime").timedelta(hours=expires_hours)
        link.save(update_fields=["expires_at"])

    shareable_url = request.build_absolute_uri(f"/sdownload/?token={link.token}")

    return JsonResponse({
        "url": shareable_url,
        "token": link.token,
        "expires_at": link.expires_at.strftime("%Y-%m-%d %H:%M UTC"),
        "max_downloads": link.max_downloads,
        "download_count": link.download_count,
    })


from django.http import JsonResponse


@never_cache
def shared_link_download(request):
    """
    GET /sdownload/?token=...
    No login required.  Validates token, increments counter, decrypts and serves file.
    """
    token = request.GET.get("token", "").strip()

    if not token:
        return HttpResponse("Missing token.", status=400)

    try:
        link = SharedLink.objects.select_related("file").get(token=token)
    except SharedLink.DoesNotExist:
        return HttpResponse("Invalid or expired link.", status=404)

    if link.is_expired:
        return HttpResponse("This link has expired.", status=410)

    if link.is_exhausted:
        return HttpResponse("Download limit reached for this link.", status=403)

    # Increment counter atomically
    SharedLink.objects.filter(pk=link.pk).update(
        download_count=F("download_count") + 1
    )

    note = link.file

    # Reuse existing decryption logic untouched
    with note.file.open("rb") as f:
        encrypted_data = f.read()

    decrypted = decrypt_data(encrypted_data, note.encryption_key.encode())

    filename = note.original_filename
    content_type, _ = mimetypes.guess_type(filename)

    temp_file = NamedTemporaryFile(delete=True)
    temp_file.write(decrypted)
    temp_file.seek(0)

    return FileResponse(
        temp_file,
        as_attachment=True,
        filename=filename,
        content_type=content_type or "application/octet-stream",
    )
