# Sentinel AI - Demo Walkthrough

Follow this "Golden Path" script to demonstrate Sentinel AI perfectly within a 3-minute window.

## Step 1: The Landing Page (0:00 - 0:30)
1. Start at the Homepage (`/`).
2. Briefly highlight the Hero section and the value proposition: "We don't just alert, we fix."
3. Click **Start Demo** to enter the application.

## Step 2: The Demo Lab (0:30 - 1:30)
1. Navigate to the **Demo Lab** from the sidebar.
2. Explain that the lab simulates a production environment (Acme Corp / Payments API).
3. Click **Trigger Scenario** under "Database Latency Spike".
4. *Wait 3 seconds.* Watch the **Investigation Timeline** appear on the right side.
5. Narrate the timeline: "The telemetry pipeline detected the anomaly, created an Incident, and dispatched a LangGraph Agent."

## Step 3: AI Root Cause Analysis (1:30 - 2:30)
1. *Wait 7 seconds.* The timeline will complete and reveal the **AI Root Cause Analysis**.
2. Read the generated story: "A deployment was completed 6 minutes before latency increased... The AI found the bad config change."
3. Point out the **Recommended Remediation** box containing the exact fix and the generated Draft Pull Request.

## Step 4: The Architecture (2:30 - 3:00)
1. Navigate to the **Architecture** page (available from the Landing Page or Sidebar).
2. Click through the components (Telemetry -> Detection -> LangGraph -> Remediation) to prove this is a deeply integrated platform, not just a thin wrapper over an LLM.

**Demo Complete!**
