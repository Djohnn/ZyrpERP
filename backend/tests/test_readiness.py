from django.test import Client, TestCase

from outbox.models import OutboxMessage


class ReadinessTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_health_returns_200(self):
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('status', data)
        self.assertIn('services', data)
        self.assertIn('database', data['services'])
        self.assertIn('cache', data['services'])

    def test_health_returns_correlation_id(self):
        response = self.client.get('/health/')
        self.assertIn('X-Correlation-ID', response.headers)

    def test_readiness_returns_200(self):
        response = self.client.get('/readiness/')
        self.assertEqual(response.status_code, 200)

    def test_readiness_includes_outbox(self):
        response = self.client.get('/readiness/')
        data = response.json()
        self.assertIn('outbox', data)
        self.assertIn('total_pending', data['outbox'])
        self.assertIn('failed_count', data['outbox'])
        self.assertIn('oldest_pending', data['outbox'])
        self.assertIn('status', data['outbox'])

    def test_readiness_reflects_pending_outbox(self):
        OutboxMessage.objects.create(
            event_type='test.event',
            aggregate_type='Test',
            aggregate_id='123',
            payload={'key': 'value'},
            status='PENDING',
        )
        response = self.client.get('/readiness/')
        data = response.json()
        self.assertEqual(data['outbox']['total_pending'], 1)

    def test_readiness_under_backlog_threshold(self):
        for i in range(50):
            OutboxMessage.objects.create(
                event_type='test.event',
                aggregate_type='Test',
                aggregate_id=str(i),
                payload={'key': 'value'},
                status='PENDING',
            )
        response = self.client.get('/readiness/')
        self.assertEqual(response.status_code, 200)

    def test_readiness_over_backlog_threshold(self):
        for i in range(150):
            OutboxMessage.objects.create(
                event_type='test.event',
                aggregate_type='Test',
                aggregate_id=str(i),
                payload={'key': 'value'},
                status='PENDING',
            )
        response = self.client.get('/readiness/')
        self.assertEqual(response.status_code, 503)

    def test_api_v1_health_reachable(self):
        response = self.client.get('/api/v1/health/')
        self.assertEqual(response.status_code, 200)

    def test_api_v1_readiness_reachable(self):
        response = self.client.get('/api/v1/readiness/')
        self.assertIn(response.status_code, [200, 503])

    def test_readiness_reports_failed_outbox(self):
        OutboxMessage.objects.create(
            event_type='test.event',
            aggregate_type='Test',
            aggregate_id='456',
            payload={'key': 'value'},
            status='FAILED',
        )
        response = self.client.get('/readiness/')
        data = response.json()
        self.assertEqual(data['outbox']['failed_count'], 1)
