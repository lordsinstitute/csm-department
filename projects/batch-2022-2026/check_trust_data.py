#!/usr/bin/env python
"""Check trust data in database - Pure Python, no shell dependencies"""
import os
import sys
import django

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hais_core.settings')
django.setup()

from trust_ethics.models import TrustMetric, EthicalAlignment
from users.models import CustomUser

def main():
    print("=" * 70)
    print("TRUST METRICS DATA CHECK")
    print("=" * 70)

    users = CustomUser.objects.all()
    print(f"\nTotal Users: {users.count()}")
    print(f"Total TrustMetrics: {TrustMetric.objects.count()}")
    print(f"Total EthicalAlignments: {EthicalAlignment.objects.count()}")

    print("\n" + "-" * 70)
    print("Data by User:")
    print("-" * 70)
    
    for user in users:
        trust_count = TrustMetric.objects.filter(user=user).count()
        ethical_count = EthicalAlignment.objects.filter(user=user).count()
        
        if trust_count > 0 or ethical_count > 0:
            print(f"\n{user.username}:")
            print(f"  TrustMetrics: {trust_count}")
            print(f"  EthicalAlignments: {ethical_count}")
            
            # Show recent trust metrics
            recent_trust = TrustMetric.objects.filter(user=user).order_by('-timestamp')[:3]
            if recent_trust:
                print("  Recent TrustMetrics:")
                for metric in recent_trust:
                    print(f"    - {metric.metric_type}: {metric.value} (confidence: {metric.confidence}, created: {metric.timestamp.strftime('%Y-%m-%d %H:%M:%S')})")
            
            # Show recent ethical alignments
            recent_ethical = EthicalAlignment.objects.filter(user=user).order_by('-timestamp')[:3]
            if recent_ethical:
                print("  Recent EthicalAlignments:")
                for alignment in recent_ethical:
                    print(f"    - {alignment.principle}: {alignment.alignment_score:.2f} (created: {alignment.timestamp.strftime('%Y-%m-%d %H:%M:%S')})")

    print("\n" + "=" * 70)
    print("✅ Data check complete!")
    print("=" * 70)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
