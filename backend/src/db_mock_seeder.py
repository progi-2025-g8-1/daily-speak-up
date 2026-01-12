import logging
import uuid
import datetime
from faker import Faker
from sqlalchemy.orm import Session
from .db import engine

logger = logging.getLogger(__name__)
NUM_MOCK_USERS = 100
MAX_MOCK_DEVICES_PER_USER = 3
MAX_USER_INTERESTS = 10
MAX_USER_STREAK = 30
FRIENDS_WITH_NON_MOCK_USER = 25
MIN_MOCK_FRIENDSHIPS = 1000
MAX_MOCK_FRIENDSHIPS = (NUM_MOCK_USERS * (NUM_MOCK_USERS - 1)) // 2  # Max possible unique pairs
MAX_MOCK_SPEECHES_PER_USER = 10
PERCENT_SPEECHES_REPORTED = 10  

def seed_users():
    """
    Seeds the database with mock users.
    """
    from .models import User
    from .models.enums import UserRole, OnboardingStatus

    PFP_URLS = [
        'https://i.ibb.co/gLmfpHWL/1e54390f4e6982d436a7d0703f22c03e.jpg',
        'https://i.ibb.co/QFf7hPMc/2c6a5fa9cdcc187a1852ab60d50befbc.jpg',
        'https://i.ibb.co/4gSv3VmL/2f38b6684d6baa25f8fb8c345d965d0b.jpg',
        'https://i.ibb.co/LDsH5pbZ/3e089183aae0ebde0a4993e576e4d63c.jpg',
        'https://i.ibb.co/SwK3vXDb/04cb8cfb16528db26de5e2b351dafc2f.jpg',
        'https://i.ibb.co/mF1v1NxM/6b03b4322c9b201a15bd608fd704b38e.jpg',
        'https://i.ibb.co/C3QPVKXV/6cc80efcf09035d7f297191b1b2baa39.jpg',
        'https://i.ibb.co/81MMZfK/6d474c7e5f0714bc018a7f9bc292d5f1.jpg',
        'https://i.ibb.co/yc8djByn/6f324a237974e89c1bb16541ea8fc5b3.jpg',
        'https://i.ibb.co/Q3h1HnSJ/8d3a8620b200c45e8be82623b3adb825.jpg',
        'https://i.ibb.co/WvC9P9sj/50c040b5296ea39079c302ba04e87f68.jpg',
        'https://i.ibb.co/WdptGc2/74dddf69cf88c6837afcdb18a8dd7c0c.jpg',
        'https://i.ibb.co/609kYKtX/652f1283c775648c746fead3370c002f.jpg',
        'https://i.ibb.co/ns4VDkrH/872dc5c41bc079e1c002785ff2e9f4ea.jpg',
        'https://i.ibb.co/SD9vSvnN/5081f07bf8a8c6108e25cfa39418f733.jpg',
        'https://i.ibb.co/wZsMd3bF/030758b551fc2bbb62960f17896883b9.jpg',
        'https://i.ibb.co/6JZ6958N/46133c8a828d388d106701cdb938e2d1.jpg',
        'https://i.ibb.co/spWQpqQs/a6f662e38d4e87895d96545491f9b2ec.jpg',
        'https://i.ibb.co/BHh3rbkF/a40546d93cc9dd4be3fee2c9d4a13ff9.jpg',
        'https://i.ibb.co/vxsvyC61/adc27e422a609848cc1c23fb3cebed05.jpg',
        'https://i.ibb.co/WNVmmVHL/af0cbac85c416434a4c14860faaeb019.jpg',
        'https://i.ibb.co/LXJHB16q/b36c59a74dd30a3fdafb3a7398f45ca8.jpg',
        'https://i.ibb.co/vxc3RYLZ/b69da59085a4192bf399a437d53e2d40.jpg',
        'https://i.ibb.co/Kc2mxwMy/cac4d01308426a032b761bc104632781.jpg',
        'https://i.ibb.co/9jHBhGc/ce51668232380f48129a10ee1b94b60e.jpg',
        'https://i.ibb.co/N6158ZT1/d82edb85011c126c9c7db80574b073f2.jpg',
        'https://i.ibb.co/4n5MrqBp/ebff945468546b151e9a6e12a13f0717.jpg',
        'https://i.ibb.co/HTp2YCnw/eefb69bac7490d2deb4747345a9aa477.jpg',
        'https://i.ibb.co/BV5CVGr2/F8-Ga2e5-XEAAUzkd.jpg',
        'https://i.ibb.co/xSFBDvnD/fb5e14d4d970814224610ce845a05837.jpg',
        'https://i.ibb.co/XkMhTWFD/fd070d5c07b7cceb491c7f8b0517e462.jpg',
        'https://i.ibb.co/tPMkxptT/no-Filter.webp'
    ]

    fake = Faker('hr_HR')
    with Session(engine) as session:
        count_existing = session.query(User).count()
        if count_existing >= NUM_MOCK_USERS:
            logger.info(f'Users table already has {count_existing} users. Skipping seeding.')
            return
        
        logger.info(f'Seeding {NUM_MOCK_USERS} mock users...')
        for _ in range(NUM_MOCK_USERS):
            user = User(
                supertokens_user_id=f"mock-{uuid.uuid4()}",
                created_at=fake.date_time_this_decade(),
                role=UserRole.USER,
                email=fake.unique.email(),
                handle=fake.unique.user_name(),
                profile_picture_url=fake.random_element(PFP_URLS),
                onboarding_status=OnboardingStatus.COMPLETED,
            )
            session.add(user)
        session.commit()


def seed_user_devices():
    """
    Seeds the database with mock user devices.
    """
    from .models import User, UserDevice

    fake = Faker()
    with Session(engine) as session:
        existing_count = session.query(UserDevice).count()
        if existing_count > MAX_MOCK_DEVICES_PER_USER:
            logger.info(f'UserDevices table already has {existing_count} entries. Skipping seeding.')
            return
        
        users = session.query(User).all()
        logger.info(f'Seeding mock devices for {len(users)} users...')
        for user in users:
            num_devices = fake.random_int(min=1, max=MAX_MOCK_DEVICES_PER_USER)
            for _ in range(num_devices):
                device = UserDevice(
                    user_id=user.id,
                    fcm_token=str(uuid.uuid4()),
                    last_used_at=fake.date_time_this_year()
                )
                session.add(device)
        session.commit()


def seed_user_interests():
    """
    Seeds the database with mock user interests.
    """
    from .models import User, Interest, UserInterest

    fake = Faker()
    with Session(engine) as session:
        existing_count = session.query(UserInterest).count()
        if existing_count > 15:
            logger.info(f'UserInterests table already has {existing_count} entries. Skipping seeding.')
            return
        
        interests = session.query(Interest).all()
        interest_ids = [interest.id for interest in interests]
        users = session.query(User).all()
        logger.info(f'Seeding mock interests for {len(users)} users...')
        for user in users:
            num_interests = fake.random_int(min=1, max=min(MAX_USER_INTERESTS, len(interest_ids)))
            sampled_interest_ids = fake.random_sample(interest_ids, num_interests)
            for interest_id in sampled_interest_ids:
                user_interest = UserInterest(
                    user_id=user.id,
                    created_at=fake.date_time_between(start_date=user.created_at, end_date='now'),
                    interest_id=interest_id
                )
                session.add(user_interest)
        session.commit()


def seed_user_streaks():
    """
    Seeds the database with mock user streaks.
    """
    from .models import User, UserStreak

    fake = Faker()
    with Session(engine) as session:
        existing_count = session.query(UserStreak).count()
        if existing_count > 0:
            logger.info(f'UserStreaks table already has {existing_count} entries. Skipping seeding.')
            return
        
        users = session.query(User).all()
        logger.info(f'Seeding mock streaks for {len(users)} users...')
        for user in users:
            streak_length = fake.random_int(min=0, max=MAX_USER_STREAK)
            if streak_length > 0:
                end_date = fake.date_between(start_date='-30d', end_date='today')
                start_date = end_date - datetime.timedelta(days=streak_length - 1)
                streak = UserStreak(
                    user_id=user.id,
                    start_date=start_date,
                    end_date=end_date,
                    ends_at=datetime.datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59, tzinfo=datetime.timezone.utc)
                )
                session.add(streak)
        session.commit()


def seed_friendships():
    """
    Seeds the database with mock friendships between users.
    """
    from .models import User, Friendship
    from .models.enums import RequestStatus

    fake = Faker()
    with Session(engine) as session:
        existing_count = session.query(Friendship).count()
        if existing_count > 0:
            logger.info(f'Friendships table already has {existing_count} entries. Skipping seeding.')
            return
        
        users = session.query(User).all()
        user_ids = [user.id for user in users]
        max_possible = (len(user_ids) * (len(user_ids) - 1)) // 2
        num_friendships = fake.random_int(min=MIN_MOCK_FRIENDSHIPS, max=min(MAX_MOCK_FRIENDSHIPS, max_possible))
        logger.info(f'Seeding {num_friendships} mock friendships...')
        friendships_set = set()
        while len(friendships_set) < num_friendships:
            user_a, user_b = fake.random_sample(user_ids, 2)
            friendship_pair = (min(user_a, user_b), max(user_a, user_b))
            if friendship_pair not in friendships_set:
                friendships_set.add(friendship_pair)
                friendship = Friendship(
                    user_id1=friendship_pair[0],
                    user_id2=friendship_pair[1],
                    created_at=fake.date_time_this_year(),
                    requested_by_id=fake.random_element(friendship_pair),
                    status=RequestStatus.ACCEPTED
                )
                session.add(friendship)
        
        session.commit()


def seed_friendships_for_non_mock_user():
    from .models import User, Friendship
    from .models.enums import RequestStatus

    fake = Faker()
    with Session(engine) as session:
        users = session.query(User).all()
        non_mock_user = session.query(User).filter(
            ~User.supertokens_user_id.like('mock-%'), 
            ~User.supertokens_user_id.like('deleted_%'),
            User.role != UserRole.ROOT
            ).first()
        existing_count = session.query(Friendship).filter(
            (Friendship.user_id1 == non_mock_user.id) | (Friendship.user_id2 == non_mock_user.id)
        ).count() if non_mock_user else 0

        if existing_count >= FRIENDS_WITH_NON_MOCK_USER:
            logger.info(f'Friendships for non-mock user already exist. Skipping seeding.')
            return

        if non_mock_user:
            mock_users = [u for u in users if u.id != non_mock_user.id]
            friends_to_add = min(FRIENDS_WITH_NON_MOCK_USER, len(mock_users))
            selected_friends = fake.random_sample(mock_users, friends_to_add)
            friendships_set = set()
            for mock_user in selected_friends:
                friendship_pair = (min(mock_user.id, non_mock_user.id), max(mock_user.id, non_mock_user.id))
                if friendship_pair not in friendships_set:
                    friendships_set.add(friendship_pair)
                    friendship = Friendship(
                        user_id1=friendship_pair[0],
                        user_id2=friendship_pair[1],
                        created_at=fake.date_time_this_year(),
                        requested_by_id=fake.random_element(friendship_pair),
                        status=RequestStatus.ACCEPTED
                    )
                    session.add(friendship)
            logger.info(f'Added {len(selected_friends)} friendships for non-mock user')
        else:
            logger.info('No non-mock user found, skipping non-mock friendships')
        session.commit()


def seed_speeches():
    """
    Seeds the database with mock speeches.
    """
    from .models import User, Speech, Interest
    from .models.enums import SpeechVisibility

    CAPTIONS = [
        'Pomalo... i sutra je novi dan za odgađanje.',
        'I\'m not arguing, I\'m just explaining why I\'m right.',
        'Nisam lijen, samo sam na \'power saving\' modu.',
        'Reality called, so I hung up.',
        'Kava: tekućina koja pokreće moj sarkazam.',
        'My bed is a magical place where I suddenly remember everything I forgot to do.',
        'Tko rano rani, cijeli dan mu se spava.',
        'I\'m on a seafood diet. I see food and I eat it.',
        'Moj mozak ima previše otvorenih tabova.',
        'Life is short. Smile while you still have teeth.'
    ]

    VIDEO_URLS = [
        'https://www.youtube.com/embed/dQw4w9WgXcQ?si=Fi3kwUYMS3oOBXUK',
        'https://www.youtube.com/embed/jnAzOioELLQ?si=9ByEQaQBKtsKkLLl',
        'https://www.youtube.com/embed/7Gbg6Z70J7E?si=yWF74V6QOTu1oTEA',
        'https://www.youtube.com/embed/ZADcpEwy8zs?si=WbOegWB58XHTnNUg',
        'https://www.youtube.com/embed/ANFmYIjptMs?si=C19jbvq_pmSXL-Ij',
        'https://www.youtube.com/embed/X4gkDPHT1bg?si=KxhN9TWgZZ6bwpWC',
        'https://www.youtube.com/embed/V9vuCByb6js?si=tidLuwKKc8rP62TO'
    ]

    fake = Faker()
    with Session(engine) as session:
        existing_count = session.query(Speech).count()
        if existing_count > 0:
            logger.info(f'Speeches table already has {existing_count} entries. Skipping seeding.')
            return
        
        users = session.query(User).all()
        interests = session.query(Interest).all()
        interest_ids = [interest.id for interest in interests]
        logger.info(f'Seeding mock speeches for {len(users)} users...')
        for user in users:
            num_speeches = fake.random_int(min=1, max=MAX_MOCK_SPEECHES_PER_USER)
            for _ in range(num_speeches):
                speech = Speech(
                    user_id=user.id,
                    caption=fake.random_element(CAPTIONS),
                    s3_url=fake.random_element(VIDEO_URLS),
                    visibility_level=SpeechVisibility.FRIENDS,
                    interest_id=fake.random_element(interest_ids)
                )
                session.add(speech)
        session.commit()


def seed_reports():
    """
    Seeds the database with mock reports.
    """
    from .models import User, Speech, Report
    
    REPORT_REASONS = [
        "Nasilan ili uznemirujući sadržaj",
        "Spam or misleading content",
        "Govor mržnje ili maltretiranje",
        "Sexual content or nudity",
        "Kršenje autorskih prava",
        "Harassment or bullying",
        "Promicanje opasnih aktivnosti",
        "Hate speech against protected groups",
        "Dezinformacije koje mogu uzrokovati štetu",
        "Child abuse or endangerment"
    ]

    fake = Faker()
    with Session(engine) as session:
        existing_count = session.query(Report).count()
        if existing_count > 0:
            logger.info(f'Reports table already has {existing_count} entries. Skipping seeding.')
            return
        
        users = session.query(User).all()
        speeches = session.query(Speech).all()
        logger.info(f'Seeding mock reports for {len(speeches)} speeches...')
        for speech in speeches:
            if fake.boolean(chance_of_getting_true=PERCENT_SPEECHES_REPORTED):
                reporting_user = fake.random_element([user for user in users if user.id != speech.user_id])
                report = Report(
                    reported_by=reporting_user.id,
                    speech_id=speech.id,
                    reason=fake.random_element(REPORT_REASONS),
                    created_at=fake.date_time_this_year()
                )
                session.add(report)
        session.commit()


def seed_ratings():
    """
    Seeds the database with mock ratings for speeches.
    """
    from .models import User, Speech, Rating

    fake = Faker()
    with Session(engine) as session:
        existing_count = session.query(Rating).count()
        if existing_count > 0:
            logger.info(f'Ratings table already has {existing_count} entries. Skipping seeding.')
            return
        
        users = session.query(User).all()
        speeches = session.query(Speech).all()
        logger.info(f'Seeding mock ratings for {len(speeches)} speeches...')
        for speech in speeches:
            other_users = [user for user in users if user.id != speech.user_id]
            num_ratings = fake.random_int(min=1, max=max(1, len(other_users) // 10))
            raters = fake.random_sample(other_users, min(num_ratings, len(other_users)))
            for rater in raters:
                rating = Rating(
                    rated_by=rater.id,
                    speech_id=speech.id,
                    score=fake.random_int(min=1, max=5),
                    created_at=fake.date_time_this_year()
                )
                session.add(rating)
        session.commit()


def seed_mock_data():
    """
    Seeds the database with mock data for testing purposes.
    """

    seed_users()
    seed_user_devices()
    seed_user_interests()
    seed_user_streaks()
    seed_friendships()
    seed_friendships_for_non_mock_user()
    seed_speeches()
    seed_reports()
    seed_ratings()