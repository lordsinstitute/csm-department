#!/usr/bin/env python
"""
Test Interaction Data Creator - Pure Python, no shell dependencies
Creates sample trust metrics for testing dashboards on any laptop
"""
import os
import sys
import django

# Add project root to path - works on any laptop
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hais_core.settings')
django.setup()

from trust_ethics.models import TrustMetric, EthicalAlignment
from users.models import CustomUser

def create_test_data():
    """Create test trust metrics and ethical alignments"""
    print("=" * 70)
    print("TEST INTERACTION DATA CREATOR")
    print("=" * 70)
    
    # Get or create test user
    user, created = CustomUser.objects.get_or_create(
        username='test_user_dashboard',
        defaults={'email': 'testuser@example.com'}
    )
    print(f"\n👤 User: {user.username} (created: {created})")
    
    # Create test trust metrics
    print("\n📊 Creating test trust metrics...")
    metrics_data = [
        ('interaction_confidence', 75.5, 0.85),
        ('interaction_confidence', 82.3, 0.90),
        ('interaction_confidence', 88.1, 0.92),
    ]
    
    created_metrics = 0
    for metric_type, value, confidence in metrics_data:
        tm = TrustMetric.objects.create(
            user=user,
            metric_type=metric_type,
            value=float(value),
            confidence=float(confidence)
        )
        print(f"  ✅ Created: {metric_type} = {value}")
        created_metrics += 1
    
    # Create test ethical alignments
    print("\n⚖️  Creating ethical alignment records...")
    principles = [
        ('Alignment', 0.85, 'Test alignment'),
        ('Transparency', 0.92, 'Test transparency'),
        ('Accountability', 0.88, 'Test accountability'),
        ('Fairness', 0.90, 'Test fairness'),
    ]
    
    created_alignments = 0
    for principle_name, score, explanation in principles:
        ea = EthicalAlignment.objects.create(
            user=user,
            principle=principle_name,
            alignment_score=float(score),
            explanation=explanation
        )
        print(f"  ✅ Created: {principle_name} = {score}")
        created_alignments += 1
    
    # Verify creation
    print("\n✨ Verification:")
    print(f"  TrustMetrics created: {created_metrics}")
    print(f"  EthicalAlignments created: {created_alignments}")
    
    # Show dashboard data like the view would
    print("\n📈 Dashboard preparation:")
    trust_metrics = TrustMetric.objects.filter(user=user).order_by('timestamp')
    trust_by_date = {}
    for metric in trust_metrics:
        date_str = metric.timestamp.strftime('%Y-%m-%d')
        if date_str not in trust_by_date:
            trust_by_date[date_str] = []
        trust_by_date[date_str].append(metric.value)
    
    trust_data = {
        'labels': sorted(trust_by_date.keys()),
        'values': [round(sum(trust_by_date[date]) / len(trust_by_date[date]), 1) for date in sorted(trust_by_date.keys())]
    }
    
    ethical_data = {
        'principles': ['Alignment', 'Transparency', 'Accountability', 'Fairness'],
        'scores': []
    }
    
    for principle in ethical_data['principles']:
        obj = EthicalAlignment.objects.filter(user=user, principle=principle).last()
        if obj:
            ethical_data['scores'].append(round(obj.alignment_score * 100, 1))
        else:
            ethical_data['scores'].append(0)
    
    print(f"  Trust Labels: {trust_data['labels']}")
    print(f"  Trust Values: {trust_data['values']}")
    print(f"  Ethical Principles: {ethical_data['principles']}")
    print(f"  Ethical Scores: {ethical_data['scores']}")
    
    print("\n" + "=" * 70)
    print("✅ TEST DATA CREATED SUCCESSFULLY!")
    print("=" * 70)
    print("\nNext steps:")
    print("  1. Start server: python manage.py runserver 8000")
    print("  2. Visit: http://127.0.0.1:8000/trust/")
    print("  3. Both charts should now display data!")
    
    return True

if __name__ == '__main__':
    try:
        create_test_data()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
