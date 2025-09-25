from django.shortcuts import render
from django.http import HttpResponse
from django.urls import reverse
from .forms import ResearchForm
from .utils.perplexity_client import PerplexityClient
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO

def home(request):
    if request.method == 'POST':
        form = ResearchForm(request.POST)
        if form.is_valid():
            topic = form.cleaned_data['topic']
            return generate_report(request, topic)
    else:
        form = ResearchForm()
    return render(request, 'research/home.html', {'form': form})

def generate_report(request, topic):
    client = PerplexityClient()
    
    # Craft targeted prompts for each research aspect
    prompts = {
        'gaps': f"Identify key market gaps and unmet needs in '{topic}'. Include data and trends.",
        'competitors': f"Analyze top 3-5 competitors in '{topic}'. Cover strengths, weaknesses, market share.",
        'opportunities': f"Find growth opportunities and actionable strategies for entering '{topic}' market.",
    }
    
    results = {}
    citations = []
    for key, prompt in prompts.items():
        try:
            answer, cites = client.query(prompt)
            results[key] = answer
            citations.extend(cites)
        except Exception as e:
            results[key] = f"Error fetching data: {str(e)}"
    
    # Generate actionable insights (simple synthesis)
    insights_prompt = f"Summarize actionable insights from: Gaps: {results['gaps']}; Competitors: {results['competitors']}; Opportunities: {results['opportunities']}."
    try:
        insights, insight_cites = client.query(insights_prompt)
        results['insights'] = insights
        citations.extend(insight_cites)
    except Exception as e:
        results['insights'] = f"Error generating insights: {str(e)}"
    
    # For PDF download, check if it's a POST (from form) or GET (preview)
    if request.method == 'POST':
        pdf_url = reverse('generate_pdf', kwargs={'topic': topic})
        return render(request, 'research/report.html', {
            'topic': topic,
            'results': results,
            'citations': citations,
            'pdf_url': pdf_url
        })
    
    # Render HTML report for preview
    return render(request, 'research/report.html', {
        'topic': topic,
        'results': results,
        'citations': citations
    })

def generate_pdf_report(request, topic):
    # Re-run the research logic for PDF (in production, cache this to avoid re-querying)
    client = PerplexityClient()
    prompts = {
        'gaps': f"Identify key market gaps and unmet needs in '{topic}'. Include data and trends.",
        'competitors': f"Analyze top 3-5 competitors in '{topic}'. Cover strengths, weaknesses, market share.",
        'opportunities': f"Find growth opportunities and actionable strategies for entering '{topic}' market.",
    }
    
    results = {}
    citations = []
    for key, prompt in prompts.items():
        try:
            answer, cites = client.query(prompt)
            results[key] = answer
            citations.extend(cites)
        except Exception as e:
            results[key] = f"Error fetching data: {str(e)}"
    
    insights_prompt = f"Summarize actionable insights from: Gaps: {results['gaps']}; Competitors: {results['competitors']}; Opportunities: {results['opportunities']}."
    try:
        insights, insight_cites = client.query(insights_prompt)
        results['insights'] = insights
        citations.extend(insight_cites)
    except Exception as e:
        results['insights'] = f"Error generating insights: {str(e)}"
    
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 50
    p.drawString(100, y, f"Deep Market Research Report: {topic}")
    y -= 30
    
    for section, content in results.items():
        p.drawString(100, y, f"{section.title().replace('_', ' ').upper()}:")
        y -= 20
        # Simple text wrapping (limited for demo)
        lines = content.split('\n')
        for line in lines[:10]:  # Limit lines per section
            wrapped_line = line[:80]  # Truncate
            p.drawString(120, y, wrapped_line)
            y -= 15
            if y < 100:  # New page if needed
                p.showPage()
                y = height - 50
        y -= 20
    
    p.drawString(100, y, "Citations:")
    y -= 20
    for cite in citations[:10]:  # Limit citations
        cite_text = f"[{cite.get('id', 'N/A')}] {cite.get('source', 'No source')[:100]}"
        p.drawString(120, y, cite_text)
        y -= 15
        if y < 100:
            p.showPage()
            y = height - 50
    
    p.save()
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="market_research_{topic.replace(" ", "_")}.pdf"'
    return response
