from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.db.models import Avg, F, ExpressionWrapper, fields
from django.utils import timezone
from .models import Case, Point, TimeTracker
import os
from .models import NewsEntry
from .forms import NewsEntryAdminForm  
from django.http import HttpResponseRedirect
import requests
import json
from django.core.mail import send_mail



class PointInline(admin.TabularInline):
    model = Point
    extra = 1
    show_change_link = True

@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ('case_id', 'assigned_at', 'get_points', 'solved_at', 'get_annotations', 'get_total_time')
    list_display_links = ('case_id',)
    search_fields = ('case_id', 'annotations', 'points__key', 'points__value')
    list_filter = ('assigned_at', 'solved_at')
    inlines = [PointInline]
    change_list_template = "admin/appnotenova/case/change_list.html"
    
    def get_points(self, obj):
        points = obj.points.all()
        formatted_points = [
            format_html('<strong>{}:</strong> {}', p.key, p.value)
            for p in points
        ]
        return format_html('<div style="max-width:300px; font-size:14px; white-space:pre-wrap;">{}</div>',
                           mark_safe('<br>'.join(formatted_points)))
    get_points.short_description = 'Points'

    def get_annotations(self, obj):
        return format_html('<div style="max-width:500px; white-space:pre-wrap;">{}</div>', obj.annotations)
    get_annotations.short_description = 'Annotations'

    def get_total_time(self, obj):
        if obj.assigned_at and obj.solved_at:
            total_minutes = (obj.solved_at - obj.assigned_at).total_seconds() / 60
            color = 'red' if total_minutes > 10 else 'green'
            return format_html('<span style="color: {};">{} minutes</span>', color, round(total_minutes, 2))
        return "N/A"
    get_total_time.short_description = 'Total Time'

    def changelist_view(self, request, extra_context=None):
        today = timezone.now().date()
        daily_cases = Case.objects.filter(assigned_at__date=today, solved_at__isnull=False)
        
        avg_time = daily_cases.aggregate(
            avg_time=Avg(ExpressionWrapper(
                F('solved_at') - F('assigned_at'),
                output_field=fields.DurationField()
            ))
        )['avg_time']

        if avg_time:
            avg_minutes = avg_time.total_seconds() / 60
            percentage = (10 / avg_minutes) * 100  # 10 minutes is the target
        else:
            avg_minutes = 0
            percentage = 100  # If no cases, assume 100% efficiency

        extra_context = extra_context or {}
        extra_context['daily_average'] = "{:.2f}%".format(percentage)
        extra_context['avg_minutes'] = "{:.2f}".format(avg_minutes) if avg_time else "N/A"
        return super().changelist_view(request, extra_context=extra_context)

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }


@admin.register(Point)
class PointAdmin(admin.ModelAdmin):
    list_display = ('case', 'key', 'value')
    list_display_links = ('case', 'key')
    search_fields = ('case__case_id', 'key', 'value')
    list_filter = ('key',)

@admin.register(TimeTracker)
class TimeTrackerAdmin(admin.ModelAdmin):
    list_display = ('break_type', 'aux_used', 'in_time', 'out_time', 'get_total_time')
    list_filter = ('break_type', 'aux_used', 'in_time', 'out_time')
    search_fields = ('break_type',)

    def get_total_time(self, obj):
        if obj.out_time and obj.in_time:
            duration = obj.out_time - obj.in_time
            minutes = duration.total_seconds() / 60
            return f"{int(minutes)} minutes"
        return "N/A"
    get_total_time.short_description = 'Total Time'





# --------------------------------------- editing on 17/01/2025 ------------------
from django.contrib import admin
from django.http import HttpResponseRedirect
from .models import NewsEntry
import requests
import json
import html2text  # Change this import

@admin.register(NewsEntry)
class NewsEntryAdmin(admin.ModelAdmin):
    list_display = ('headline', 'created_at')
    search_fields = ('headline', 'paragraph')
    readonly_fields = ('created_at',)

    def send_to_chime(self, obj):
        webhook_url = "https://hooks.chime.aws/incomingwebhooks/21d7ffa3-6a29-4ea9-85e8-c3a6bfd05751?token=TmJzaFlNbUp8MXx4Z0FiQTZ5N0xjT09rNm8wTGtLRjNnVkZyaDNvN2pncmMtOW8zOXc3YTZV"
        formatted_date = obj.created_at.strftime('%Y-%m-%d')
        
        # Configure html2text
        h = html2text.HTML2Text()
        h.body_width = 0  # Don't wrap text
        h.unicode_snob = True  # Use Unicode
        h.tables = True  # Enable table formatting
        
        # Convert HTML to Markdown
        markdown_content = h.handle(obj.paragraph)
        
        message = {
            "Content": f"/md # {obj.headline}\n\n{markdown_content}\n\n_Posted on: {formatted_date}_"
        }

        try:
            response = requests.post(
                webhook_url,
                data=json.dumps(message),
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error sending to Chime: {str(e)}")
            return False

    def response_change(self, request, obj):
        if "_save_and_chime" in request.POST:
            if self.send_to_chime(obj):
                self.message_user(request, "Entry saved and sent to Chime successfully!")
            else:
                self.message_user(request, "Entry saved but failed to send to Chime!")
            return HttpResponseRedirect(".")
        return super().response_change(request, obj)

    def response_add(self, request, obj, post_url_continue=None):
        if "_save_and_chime" in request.POST:
            if self.send_to_chime(obj):
                self.message_user(request, "Entry saved and sent to Chime successfully!")
            else:
                self.message_user(request, "Entry saved but failed to send to Chime!")
            return HttpResponseRedirect(".")
        return super().response_add(request, obj, post_url_continue)

