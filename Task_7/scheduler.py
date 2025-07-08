#!/usr/bin/env python3

import schedule
import time
from datetime import datetime
from main import main

def scheduled_newsletter():
    """Function to run scheduled newsletter generation"""
    print(f"\n⏰ Scheduled newsletter generation started at {datetime.now()}")
    try:
        main()
        print(f"✅ Scheduled newsletter completed at {datetime.now()}")
    except Exception as e:
        print(f"❌ Scheduled newsletter failed: {e}")

def run_scheduler():
    """Run the scheduler for daily newsletter generation"""
    print("🕐 Starting Newsletter Scheduler...")
    print("📅 Newsletter will be generated daily at 9:00 AM")
    print("🔄 For demo purposes, also running every 2 minutes...")
    
    # Schedule daily at 9 AM
    schedule.every().day.at("09:00").do(scheduled_newsletter)
    
    # For demo purposes - run every 2 minutes
    schedule.every(2).minutes.do(scheduled_newsletter)
    
    print("✅ Scheduler started. Press Ctrl+C to stop.")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Scheduler stopped by user.")

if __name__ == "__main__":
    run_scheduler()