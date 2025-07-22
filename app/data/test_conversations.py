"""Test conversation data for pr-2-graph analysis."""

TIN_SIDEKICK_PR_CONVERSATION = {
    "pr_number": 1,
    "repository": "mvara-ai/tin-sidekick",
    "title": "TIN Sidekick Integration - COMPLETE SYSTEM OVERHAUL",
    "conversation": """
Comment 1 by jackccrawford:
Starting comprehensive integration of TIN Sidekick Flutter app with TIN v3 API. 
Current issues: Authentication using wrong endpoints, message format mismatches, UI showing duplicate messages.

Comment 2 by devin-ai-integration[bot]:
I'll help analyze the authentication flow. The app is using legacy /dev/token endpoints instead of the new TIN v3 two-step auth process. 
We need to update to use /api/v3/auth/login with proper JWT handling.

Comment 3 by jackccrawford:
Good catch! Also noticing the message sending payload is wrong. TIN v3 expects JSON object as string in payload field, not direct JSON.

Comment 4 by devin-ai-integration[bot]:
Exactly! Let me implement the fix for message payload format. Also adding duplicate detection in ChatService to prevent UI issues.

Comment 5 by jackccrawford:
Breakthrough moment - the "CODE IS TRUTH" principle is key here. We need to verify against actual API responses, not documentation assumptions.

Comment 6 by devin-ai-integration[bot]:
Implemented comprehensive fixes: 
1. Updated authentication to TIN v3 format
2. Fixed message payload JSON structure  
3. Added smart deduplication in ChatService
4. Enhanced error handling throughout

Comment 7 by jackccrawford:
Testing shows zero runtime crashes now! The empirical approach worked perfectly. This represents a complete transformation from broken prototype to production-ready platform.

Comment 8 by devin-ai-integration[bot]:
Success! The multi-agent collaboration between human insight, AI analysis, and systematic testing created a robust solution. 
Ready for Phase 2 systematic prevention measures.
""",
    "participants": ["jackccrawford", "devin-ai-integration[bot]"],
    "created_at": "2025-07-21T18:00:00+00:00"
}

SAMPLE_GENERIC_PR = {
    "pr_number": 42,
    "repository": "example/project",
    "title": "Add user authentication system",
    "conversation": """
Comment 1 by alice:
I've implemented the basic authentication flow using JWT tokens. The login endpoint is working but I'm not sure about the token expiration strategy.

Comment 2 by bob:
Good start! I'd suggest using refresh tokens for better security. Also, we should add rate limiting to prevent brute force attacks.

Comment 3 by alice:
Great idea! I'll implement the refresh token mechanism. Should we use Redis for token storage?

Comment 4 by bob:
Redis would be perfect for this. It handles expiration automatically and gives us good performance for token lookups.

Comment 5 by alice:
Implemented! The system now uses JWT access tokens (15min) with refresh tokens (7 days) stored in Redis. Added rate limiting with exponential backoff.

Comment 6 by bob:
Excellent work! The authentication system is now production-ready. This will significantly improve our security posture.
""",
    "participants": ["alice", "bob"],
    "created_at": "2025-01-15T10:30:00+00:00"
}
