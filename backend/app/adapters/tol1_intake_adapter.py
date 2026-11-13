"""TOL1 intake adapter stub."""


class TOL1IntakeAdapter:
    """
    Adapter for TOL1 multi-channel intake connector.

    Placeholder for event-driven intake from:
    - RFP document store
    - Email inbox
    - Phone note capture
    - Supplier offer inbox
    """

    def __init__(self):
        pass

    def fetch_pending_submissions(self, channel_type: str | None = None) -> list[dict]:
        """
        Fetch pending submissions from TOL1 channels.

        Placeholder implementation. In production, this would:
        - Poll or subscribe to intake channels
        - Retrieve unprocessed artifacts
        - Return normalized submission payloads
        """
        return []

    def acknowledge_submission(self, submission_id: str) -> bool:
        """
        Acknowledge processing of a submission.

        Placeholder implementation.
        """
        return True
