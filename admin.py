from django.contrib import admin
import django.forms as forms
from django.contrib.contenttypes import generic
from DublinCore.models import QualifiedDublinCoreElement
from collection_record.models import CollectionRecord

class QDCElementInlineForm(forms.ModelForm):
    class Meta:
        model = QualifiedDublinCoreElement
    def __init__(self, *args, **kwargs):
        super(QDCElementInlineForm, self).__init__(*args, **kwargs)
        self.fields['term'] = forms.ChoiceField(choices=(('-','------'),)+QualifiedDublinCoreElement.DCELEMENTS)

class QDCElementInline(generic.GenericTabularInline):
    model = QualifiedDublinCoreElement
    extra = 0
    form = QDCElementInlineForm

class CollectionRecordAdmin(admin.ModelAdmin):
    #readonly_fields = ('ark', ) #Had to remove to allow adding through admin
    # still guarded in the CollectionRecord.save() method
    search_fields = ('ark', 'title', 'abstract')
    list_display = ('ark', 'title' , 'abstract', 'updated_at', 'created_at', )
    #list_filter = ('', )
    inlines = (QDCElementInline, )
    save_on_top = True
admin.site.register(CollectionRecord, CollectionRecordAdmin)