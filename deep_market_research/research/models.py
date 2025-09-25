from django.db import models

class MarketReport(models.Model):
    topic = models.CharField(max_length=200)
    report_content = models.TextField()
    citations = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    insights = models.TextField(blank=True)

    def __str__(self):
        return f"Report for {self.topic}"
