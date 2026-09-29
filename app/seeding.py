import asyncio
import random
import sys
from datetime import UTC

from faker import Faker
from sqlalchemy import select

from app.auth.service import hash_password
from app.core.database import async_session

from .models import Organization, Post, User, UserRole

fake = Faker()

async def seed_users(n: int):
    async with async_session() as session:
        result = await session.execute(select(Organization.uid))
        org_ids = list(result.scalars().all())

        if not org_ids:
            print(" No organization found! Please create an organization first.")
            return

        print(f"Creating {n} fake users...")

        # default password for all seeded user (e.g. all users get 'password123')
        default_hash = hash_password("password123")

        # Generate fake users
        users = []
        for _ in range(n):
            user = User(
                username=fake.user_name(),
                email=fake.unique.email(),
                hashed_password=default_hash,  
                is_verified=True,              
                role=UserRole.USER,
                organization_id=random.choice(org_ids),  # random organization_id
            )
            users.append(user)

        session.add_all(users)
        await session.commit()
        print(f" Successfully seeded {n} users! (Password for all: 'password123')")


async def seed_posts_for_all_users(posts_per_user: int):
    async with async_session() as session:

        result = await session.execute(select(User.id))
        user_ids = list(result.scalars().all())
        if not user_ids:
            print("[ERROR] No users found in the database! Please create or seed users first.")
            return
        total_posts = len(user_ids) * posts_per_user
        print(f"Found {len(user_ids)} users. Generating {posts_per_user} posts for each user ({total_posts} total posts)...")
        
        for index, uid in enumerate(user_ids, start=1):
            posts = [
                Post(
                    title=fake.sentence(nb_words=6).rstrip("."),
                    content=fake.paragraph(nb_sentences=4),
                    user_id=uid,
                    created_at=fake.date_time_between(start_date="-1y", end_date="now", tzinfo=UTC),
                )
                for _ in range(posts_per_user)
            ]
            
            session.add_all(posts)
            await session.commit()
            print(f"[{index}/{len(user_ids)}] Created {posts_per_user} posts for User ID: {uid}")
        print(f"[SUCCESS] Finished! Inserted {total_posts} posts across {len(user_ids)} users.")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(seed_users(1000))
    asyncio.run(seed_posts_for_all_users(1000))