#from django.test import TestCase
#from rest_framework.test import APIClient
#
#class TestConnectionPostGet(TestCase):
#
#    def test_post_method(self):
#        factory = APIClient()
#        request = factory.post('/geoserver/teste/',{'PAT':'Token'}, format='json')
#        assert request.status_code == 200
#
#        request2 = factory.post('/geoserver/teste/', {'PTA':'Token','color':'blue'}, format='json')
#        assert request2.status_code != 200