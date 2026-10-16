"""Assign explicitly selected pre-authentication businesses to an existing user.

Run only as a database administrator after verifying the target user's identity and
business IDs. This is deliberately not exposed as a public API endpoint.
"""
from __future__ import annotations

import argparse
from uuid import UUID

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.business import Business
from app.models.user import BusinessMembership, User


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--email", required=True, help="Existing account email that should own the business(es).")
    parser.add_argument(
        "--business-id", required=True, action="append", type=UUID,
        help="Exact legacy business UUID to assign. Repeat for each verified business.",
    )
    args = parser.parse_args()

    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == args.email.strip().lower()))
        if user is None:
            parser.error("No account exists for that email. Register and verify the target account first.")

        missing: list[str] = []
        assigned: list[str] = []
        for business_id in args.business_id:
            business = db.get(Business, business_id)
            if business is None:
                missing.append(str(business_id))
                continue
            membership = db.scalar(
                select(BusinessMembership).where(
                    BusinessMembership.user_id == user.id,
                    BusinessMembership.business_id == business.id,
                )
            )
            if membership is None:
                db.add(BusinessMembership(user_id=user.id, business_id=business.id, role="owner"))
                assigned.append(f"{business.name} ({business.id})")
        if missing:
            db.rollback()
            parser.error("Unknown business UUID(s): " + ", ".join(missing) + ". No assignments were saved.")
        db.commit()
        print(f"Account: {user.email}")
        print(f"New ownership assignments: {len(assigned)}")
        for item in assigned:
            print(f"  - {item}")
        print("Existing memberships were left unchanged.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
