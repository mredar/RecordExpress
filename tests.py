import os
from urllib import quote
import xml.etree.ElementTree as ET
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.db.models.base import ValidationError
from django_webtest import WebTest
from collection_record.forms import CollectionRecordForm
from collection_record.models import CollectionRecord

class CollectionRecordModelTest(TestCase):
    '''Test the CollectionRecord django model'''
    fixtures = ['collection_record.collectionrecord.json', 'collection_record.dublincore.json', 'oac.institution.json', 'oac.groupprofile.json']#['sites.json', 'auth.json', 

    def testModelExists(self):
        rec = CollectionRecord()
        self.failUnlessRaises(ValidationError, rec.full_clean)

    def testEZID_DublinCoreUpdate(self):
        '''Test that the Dublin Core attrs of the EZID get updateed by 
        a save of the object.
        '''
        pass

    def testEAD_xml_output(self):
        '''Test the ead string output for a CollectionRecord. Check unicode
        support
        '''
        rec = CollectionRecord.objects.get(pk=1)
        ead_xml = rec.ead_xml
        self.failUnless(ead_xml.index('<?xml') == 0)
        self.failUnless(ead_xml.index('<ead>') == 162)
        self.failUnless('ark:/13030/c8s180ts' in ead_xml)
        self.failUnless('persname' in ead_xml)
        self.failUnless('<physdesc label="Extent">' in ead_xml)
        self.failUnless('<repository label="' in ead_xml)
        self.failUnless('<abstract label="Abstract">' in ead_xml)
        self.failUnless('<langmaterial><language langcode="' in ead_xml)
        self.failUnless('<accessrestrict><head>Access</head><p>' in ead_xml)
        self.failUnless('<userestrict><head>Publication Rights</head><p>' in ead_xml)
        self.failUnless('<prefercite><head>Preferred Citation</head>' in ead_xml)
        self.failUnless('<acqinfo><head>Acquisition Information</head>' in ead_xml)
        self.failUnless('<bioghist><head>Biography/Administrative History</head>' in ead_xml)
        self.failUnless('<scopecontent><head>Scope and Content of Collection</head>' in ead_xml)
        self.failUnless('<controlaccess>' in ead_xml)
        self.failUnless('</archdesc>' in ead_xml)
        self.failUnless('</ead>' in ead_xml)
        try:
            ET.fromstring(ead_xml)
        except:
            self.fail('ElementTree could not parse xml')
        print ead_xml


class CollectionRecordFormTestCase(TestCase):
    '''Test the form for creating new collection records. Is this form different
    from the existing record form?
    '''
    def testNewForm(self):
        f = CollectionRecordForm()
     

class NewCollectionRecordViewTestCase(WebTest):
    fixtures = ['sites.json', 'auth.json', 'oac.institution.json', 'oac.groupprofile.json']
    def setUp(self):
        '''Override the "databases" config file to use the test shoulder'''
        os.environ['DATABASES_XML_FILE'] = os.path.join(os.environ['HOME'], '.databases-test.xml')

    def testNewView(self):
        '''Test the view for creating new collection records.
        View needs to be login protected.
        '''
        url = reverse('collection_record_add')
        response = self.app.get(url)
        self.failUnlessEqual('302 FOUND', response.status)
        self.failUnlessEqual(302, response.status_code)
        self.assertRedirects(response, '/accounts/login/?next='+quote(url))
        response = self.app.get(url, user='oactestuser')
        self.failUnlessEqual(200, response.status_code)
        self.assertContains(response, 'itle')
        self.assertContains(response, '<option value="eng" selected="selected">English</option>')
        self.assertContains(response, 'access')
        self.assertContains(response, 'CR')
        self.assertContains(response, 'person')
        self.assertContains(response, 'family')
        form = response.form
        response = form.submit(user='oactestuser')
        self.failUnlessEqual(200, response.status_code)
        self.assertTemplateUsed(response,'collection_record/collection_record/add.html') 
        form = response.form
        #fill out basic info only,required fields only
        form['title'] = 'Test Title'
        form['title_filing'] = 'Test Filing Title'
        form['date_dacs'] = 'circa 1980'
        form['date_iso'] = '1980'
        form['local_identifier'] = 'LOCALID-test'
        form['extent'] = 'loads of boxes'
        form['abstract'] = 'a nice test collection'
        form['accessrestrict'] = 'public domain'
        form['userestrict'] = 'go craxy'
        form['acqinfo'] = 'by mark'
        form['scopecontent'] = 'test content'
        response = form.submit(user='oactestuser')
        self.assertTemplateUsed(response,'collection_record/collection_record/add_preview.html') 
        response = response.form.submit(user='oactestuser')
        self.failUnlessEqual(302, response.status_code)
        response = response.follow()
        self.failUnlessEqual(200, response.status_code)
        self.assertContains(response, 'ark:')
        self.assertContains(response, 'Test Title')
        self.assertTemplateUsed(response,'collection_record/collection_record/view.html') 

    def testNewWithDCView(self):
        url = reverse('collection_record_add')
        response = self.app.get(url, user='oactestuser')
        self.failUnlessEqual(200, response.status_code)
        form = response.form
        #fill out basic info only,required fields only
        form['title'] = 'Test 2 Title'
        form['title_filing'] = 'Test Filing Title'
        form['date_dacs'] = 'circa 1980'
        form['date_iso'] = '1980'
        form['local_identifier'] = 'LOCALID-test'
        form['extent'] = 'loads of boxes'
        form['abstract'] = 'a nice test collection'
        form['accessrestrict'] = 'public domain'
        form['userestrict'] = 'go craxy'
        form['acqinfo'] = 'by mark'
        form['scopecontent'] = 'test content'
        form['person-0-content'] = 'mark redar'
        form['family-0-content'] = 'redar'
        response = form.submit(user='oactestuser')
        self.assertTemplateUsed(response,'collection_record/collection_record/add_preview.html') 
        response = response.form.submit(user='oactestuser')
        self.failUnlessEqual(302, response.status_code)
        response = response.follow()
        self.failUnlessEqual(200, response.status_code)
        self.assertContains(response, 'ark:')
        self.assertContains(response, 'Test 2 Title')
        self.assertContains(response, 'redar')
        self.assertTemplateUsed(response,'collection_record/collection_record/view.html') 
