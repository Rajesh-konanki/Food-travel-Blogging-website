import re

from werkzeug.security import generate_password_hash

from app import app
from config import Config
from extensions import db
from models import Category, Comment, Post, Tag, User
from utils import unique_slug


CATEGORIES = [
    {"name": "Street Food", "slug": "street-food", "description": "Best street food around the world"},
    {"name": "Travel Guides", "slug": "travel-guides", "description": "Complete travel guides for every destination"},
    {"name": "Restaurants", "slug": "restaurants", "description": "Top restaurant reviews worldwide"},
    {"name": "Adventure", "slug": "adventure", "description": "Thrilling adventure travel experiences"},
    {"name": "Local Cuisine", "slug": "local-cuisine", "description": "Authentic local food experiences"},
    {"name": "Beach Getaways", "slug": "beach-getaways", "description": "Best beach destinations worldwide"},
]

TAGS = [
    "Italy",
    "Japan",
    "India",
    "Thailand",
    "Paris",
    "Pizza",
    "Sushi",
    "Curry",
    "Pasta",
    "Tacos",
    "Backpacking",
    "Luxury",
    "Budget Travel",
    "Solo Travel",
    "Foodie",
    "Street Food",
    "Adventure",
]

SAMPLE_POSTS = [
    {
        "title": "10 Must-Try Street Foods in Bangkok",
        "excerpt": "From Pad Thai to Mango Sticky Rice, Bangkok's street food scene is unmatched. Here's your ultimate guide to eating like a local.",
        "content": """
Bangkok is a paradise for food lovers. The moment you step off the plane,
the aroma of lemongrass, chili, and coconut milk fills the air. The city's
street food scene is legendary — from sizzling woks at night markets to
fresh fruit carts lining every corner.

**Pad Thai at Thip Samai**
No trip to Bangkok is complete without trying Pad Thai at Thip Samai,
often called the best in the world. The noodles are wok-fried to perfection
with shrimp, tofu, egg, and a squeeze of lime.

**Tom Yum Goong**
This spicy and sour shrimp soup is Bangkok's soul food. Best enjoyed at a
roadside stall with a cold Chang beer.

**Mango Sticky Rice**
The perfect dessert — sweet glutinous rice with fresh mango and coconut cream.
Find it at Or Tor Kor Market for the freshest version.
        """,
        "cover_image": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800",
        "category": "street-food",
        "tags": ["Thailand", "Street Food", "Foodie"],
        "status": "published",
        "views": 1240,
    },
    {
        "title": "A Week in Tuscany: Food, Wine & Rolling Hills",
        "excerpt": "Tuscany is the ultimate food and travel destination. Discover the best trattorias, vineyards, and hilltop villages on this unforgettable journey.",
        "content": """
There is nowhere on earth quite like Tuscany. The golden light, the cypress
trees, the rolling green hills — it feels like stepping into a Renaissance
painting. But beyond the scenery, Tuscany is one of the world's greatest
food destinations.

**Bistecca alla Fiorentina**
This giant Florentine T-bone steak is a carnivore's dream. At least
3cm thick, cooked rare over a wood fire, seasoned with nothing but
salt and olive oil.

**Chianti Wine Country**
Rent a bike and cycle through the Chianti wine region. Stop at family-run
wineries for tastings of Sangiovese and Vernaccia.

**Truffle Hunting in San Miniato**
Join a truffle hunter and their dog for an early morning hunt through the
oak forests. Finish with a truffle pasta lunch that you'll dream about forever.
        """,
        "cover_image": "https://images.unsplash.com/photo-1523906834658-6e24ef2386f9?w=800",
        "category": "travel-guides",
        "tags": ["Italy", "Luxury", "Foodie"],
        "status": "published",
        "views": 980,
    },
    {
        "title": "Tokyo on a Budget: Eat Like a King for $20/Day",
        "excerpt": "Tokyo has some of the world's best food at shockingly affordable prices. Here's how to eat incredibly well without breaking the bank.",
        "content": """
Tokyo is a foodie's dream destination — and surprisingly affordable if you
know where to look. Forget expensive sushi restaurants; the best meals in
Tokyo are found in tiny ramen shops, standing sushi bars, and convenience
stores.

**Ramen at Ichiran**
Ichiran's solo dining booths are a Tokyo institution. Order a rich tonkotsu
broth with thick noodles and customize every element of your bowl.

**7-Eleven Onigiri**
Japan's convenience stores are legendary. Pick up rice balls, egg salad
sandwiches, and hot oden for a meal under $3.

**Tsukiji Outer Market**
Wake up early and head to Tsukiji for the freshest sushi breakfast of your
life. A tuna nigiri set costs around $8 and tastes like heaven.
        """,
        "cover_image": "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=800",
        "category": "travel-guides",
        "tags": ["Japan", "Budget Travel", "Sushi"],
        "status": "published",
        "views": 2100,
    },
    {
        "title": "The Best Pizza in Naples: A Street-by-Street Guide",
        "excerpt": "Naples is the birthplace of pizza. We ate at 14 pizzerias in 3 days so you don't have to. Here are the absolute best.",
        "content": """
If you care about pizza — and you should — then Naples is your holy land.
This chaotic, beautiful, slightly dangerous city gave the world one of its
greatest gifts, and eating pizza here is a spiritual experience.

**L'Antica Pizzeria da Michele**
The most famous pizzeria in the world. They serve only two types:
Margherita and Marinara. The queue stretches around the block but it is
absolutely worth the wait.

**Pizzeria Sorbillo**
A close second, with more variety and slightly shorter queues. Try the
Margherita Extra with buffalo mozzarella and San Marzano tomatoes.

**Port'Alba — The World's Oldest Pizzeria**
Dating back to 1738, Port'Alba is where it all began. The pizza is
traditional, charred at the edges, soft in the middle, and deeply satisfying.
        """,
        "cover_image": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800",
        "category": "restaurants",
        "tags": ["Italy", "Pizza", "Foodie"],
        "status": "published",
        "views": 1560,
    },
    {
        "title": "Surfing, Spices & Sunsets: 2 Weeks in Bali",
        "excerpt": "Bali has everything — world-class surf, stunning temples, lush rice terraces, and some of the most vibrant food on earth.",
        "content": """
Bali is one of those places that gets into your soul. The air smells of
incense and frangipani. The sunsets over Tanah Lot are impossibly beautiful.
And the food — oh, the food.

**Nasi Goreng at Warung Babi Guling**
Bali's signature dish of fried rice with suckling pig is best eaten at a
simple roadside warung. Crispy pork skin, fragrant rice, sambal — perfection.

**Ubud Food Tour**
Hire a local guide for a food tour of Ubud's morning market. Sample fresh
jackfruit, black rice pudding, and sate lilit (minced fish satay).

**Catching Waves at Uluwatu**
After days of eating, balance it out with a surf lesson at Uluwatu. The
waves are world-class and the clifftop warungs serve cold Bintangs
with the best view on earth.
        """,
        "cover_image": "https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=800",
        "category": "beach-getaways",
        "tags": ["Backpacking", "Budget Travel", "Foodie"],
        "status": "published",
        "views": 1890,
    },
    {
        "title": "Mumbai's Iconic Vada Pav: The $0.20 Meal That Rules the City",
        "excerpt": "Mumbai's unofficial street food king — the humble vada pav — is a spicy potato dumpling in a bread roll that costs less than a candy bar.",
        "content": """
Ask any Mumbaikar about their favourite food and 9 out of 10 will say
Vada Pav. This gloriously simple snack — a spiced potato patty fried in
chickpea batter, stuffed into a soft white roll with green chutney and
dry garlic powder — is the heartbeat of the city.

**Ashok Vada Pav, Dadar**
The most legendary vada pav stall in Mumbai. Queues form from 7am and
they sell out by noon. One bite and you'll understand why.

**Kirti College Canteen**
The college canteen version is softer, spicier, and served with extra
chutney. Students and office workers line up together in perfect harmony.

**How to Eat It**
Eat it standing up, at a street stall, with a cutting chai on the side.
Do not sit in a restaurant for vada pav. That defeats the whole purpose.
        """,
        "cover_image": "https://images.unsplash.com/photo-1606491956689-2ea866880c84?w=800",
        "category": "street-food",
        "tags": ["India", "Street Food", "Budget Travel"],
        "status": "published",
        "views": 3200,
    },
    {
        "title": "Kyoto in Cherry Blossom Season: Food & Temple Trail",
        "excerpt": "Kyoto transforms into a pink wonderland every spring. Here's the perfect food and sightseeing itinerary for cherry blossom season.",
        "content": """
There is no more beautiful sight in travel than Kyoto's cherry blossoms
in full bloom. The pale pink petals drift over ancient temples, zen gardens,
and stone lanterns in a scene of breathtaking, fleeting beauty.

**Philosopher's Path Picnic**
Pack a bento box from Nishiki Market and stroll the Philosopher's Path
under a canopy of cherry blossoms. Stop for matcha soft serve from a
canal-side stall.

**Kaiseki at Kikunoi**
Splurge on one kaiseki meal — Japan's refined multi-course cuisine.
Kikunoi in Higashiyama serves a spring menu with cherry blossom-themed
dishes that are edible art.

**Fushimi Inari at Dawn**
Wake at 5am and hike the thousand torii gates of Fushimi Inari before
the crowds arrive. Reward yourself with a bowl of kitsune udon at the
base of the mountain.
        """,
        "cover_image": "https://images.unsplash.com/photo-1528360983277-13d401cdc186?w=800",
        "category": "travel-guides",
        "tags": ["Japan", "Luxury", "Solo Travel"],
        "status": "published",
        "views": 1450,
    },
    {
        "title": "Paris Café Culture: The Art of Doing Nothing Beautifully",
        "excerpt": "In Paris, sitting at a café for three hours with one coffee is not laziness — it is a way of life. Here's how to live it properly.",
        "content": """
The Parisian café is one of civilization's greatest inventions. It is
a place to think, to watch the world, to write, to argue about politics,
to fall in love, to recover from heartbreak. And to eat very good croissants.

**Café de Flore, Saint-Germain**
The most literary café in Paris. Sartre and de Beauvoir wrote here.
Order a café crème and a croque monsieur and stay for at least two hours.

**Le Marais Bakeries**
Wander Le Marais at 8am for the best pastry crawl in the world.
Du Pain et des Idées makes the finest croissants in Paris — flaky,
buttery, deeply golden.

**Seine-side Picnic**
Buy a baguette, some aged comté, a bottle of Bordeaux, and a punnet
of strawberries. Sit on the banks of the Seine at sunset. This is Paris.
        """,
        "cover_image": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800",
        "category": "travel-guides",
        "tags": ["Paris", "Luxury", "Foodie"],
        "status": "published",
        "views": 1100,
    },
    {
        "title": "Thailand's Floating Markets: A Feast for All the Senses",
        "excerpt": "Damnoen Saduak and Amphawa floating markets are unlike anything else on earth — colourful boats loaded with fresh food on jungle canals.",
        "content": """
On a misty morning, colourful wooden boats glide silently through
narrow canals fringed with tropical greenery. Each boat is piled high
with fresh coconuts, grilled corn, pad thai, and boat noodles.

**Amphawa Weekend Market**
Less touristy than Damnoen Saduak, Amphawa is where locals come on
weekends. Eat grilled river prawns directly from the boat, giant
as your hand, charred and sweet.

**Boat Noodles**
The classic floating market dish — small bowls of rich pork or beef
broth with thin rice noodles. Eat five or six bowls for a full meal.

**Firefly Boat Tour**
As night falls, take a longtail boat tour to see millions of fireflies
lighting up the riverside mangroves. One of the most magical things
you will ever see.
        """,
        "cover_image": "https://images.unsplash.com/photo-1552465011-b4e21bf6e79a?w=800",
        "category": "local-cuisine",
        "tags": ["Thailand", "Street Food", "Adventure"],
        "status": "published",
        "views": 870,
    },
    {
        "title": "Hiking the Cinque Terre: Pasta, Pesto & Sea Views",
        "excerpt": "Five cliffside villages on the Italian Riviera, connected by hiking trails and united by the world's best pesto. A perfect food and adventure trip.",
        "content": """
The Cinque Terre — five tiny, colourful villages clinging to the cliffs
of the Italian Riviera — is one of Europe's most spectacular hiking
destinations. And when you arrive in each village, the food reward
is extraordinary.

**Trofie al Pesto in Monterosso**
Cinque Terre is the home of Ligurian pesto — basil, pine nuts, parmesan,
garlic, and local olive oil. The trofie pasta here tastes nothing like
pesto anywhere else in the world.

**Focaccia in Vernazza**
Pick up a slab of fresh focaccia — soft, oily, dimpled, topped with
olives or onions — from a bakery in Vernazza. Eat it on the harbour wall
watching fishing boats come in.

**Sciacchetrà Wine**
This rare, sweet dessert wine is made only in the Cinque Terre from
dried Bosco grapes. Try it at sunset in Manarola with a view of the
most photographed village in Italy.
        """,
        "cover_image": "https://images.unsplash.com/photo-1534430480872-3498386e7856?w=800",
        "category": "adventure",
        "tags": ["Italy", "Adventure", "Pasta"],
        "status": "published",
        "views": 760,
    },
    {
        "title": "The Perfect Curry Trail Across South India",
        "excerpt": "From Kerala's coconut fish curry to Tamil Nadu's chettinad chicken, South India's regional cuisines are among the most complex on earth.",
        "content": """
South India is one of the world's great culinary regions. Each state —
Kerala, Tamil Nadu, Karnataka, Andhra Pradesh — has its own distinct
cuisine, spice palette, and cooking traditions that stretch back centuries.

**Kerala Sadya**
The ultimate South Indian feast — a banana leaf spread with 20+ dishes
including avial, sambhar, rasam, payasam, and Kerala red rice. Eaten
with your right hand only.

**Chettinad Chicken Curry**
From the Chettinad region of Tamil Nadu, this is one of India's most
complex curries — kalpasi, marathi mokku, star anise, and freshly ground
spices. Fiery and unforgettable.

**Mysore Masala Dosa**
The gold standard of South Indian breakfast — a giant crispy fermented
crepe filled with spiced potato, served with coconut chutney and sambar.
        """,
        "cover_image": "https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=800",
        "category": "local-cuisine",
        "tags": ["India", "Curry", "Solo Travel"],
        "status": "published",
        "views": 2800,
    },
    {
        "title": "Greek Islands Hopping: Octopus, Ouzo & Endless Blue",
        "excerpt": "Santorini, Mykonos, Naxos, Paros — hopping the Greek Islands by ferry with a focus on the freshest seafood and whitewashed village tavernas.",
        "content": """
There is a particular quality of light in the Greek Islands that makes
everything look like a postcard. The white cubic houses, the blue domed
churches, the deep Aegean blue — all of it looks too perfect to be real.

**Grilled Octopus in Naxos**
Find a tiny taverna by the water in Naxos and order the grilled octopus —
sun-dried, then charcoal-grilled with lemon and olive oil. Eat it with
cold Assyrtiko white wine.

**Santorini Tomatoes**
The volcanic soil of Santorini produces the most intensely flavoured
cherry tomatoes on earth. Tomatokeftedes — fried tomato fritters —
are the ultimate Santorini snack.

**Loukoumades in Athens**
Before you leave Greece, eat a bowl of loukoumades — tiny hot
doughnuts drizzled with honey, cinnamon, and crushed walnuts — from
a street stall near Monastiraki.
        """,
        "cover_image": "https://images.unsplash.com/photo-1533105079780-92b9be482077?w=800",
        "category": "beach-getaways",
        "tags": ["Luxury", "Adventure", "Foodie"],
        "status": "published",
        "views": 1320,
    },
]


def format_post_content(raw: str) -> str:
    raw = raw.strip()
    blocks = re.split(r"\n\s*\n", raw)
    out = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        lines = []
        for line in block.split("\n"):
            line = line.strip()
            line = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", line)
            lines.append(line)
        inner = "<br>\n".join(lines)
        out.append(f"<p>{inner}</p>")
    return "\n".join(out)


def seed():
    with app.app_context():
        db.create_all()

        Comment.query.delete()
        Post.query.delete()
        Tag.query.delete()
        Category.query.delete()
        db.session.commit()

        admin = User.query.filter_by(email="admin@example.com").first()
        if not admin:
            admin = User(
                username="admin",
                email="admin@example.com",
                password_hash=generate_password_hash("admin123"),
                avatar=Config.AVATAR_DEFAULT,
                role="admin",
            )
            db.session.add(admin)
            db.session.flush()
        else:
            admin.avatar = admin.avatar or Config.AVATAR_DEFAULT

        categories_by_slug = {}
        for cat in CATEGORIES:
            c = Category(
                name=cat["name"],
                slug=cat["slug"],
                description=cat.get("description", ""),
            )
            db.session.add(c)
            categories_by_slug[cat["slug"]] = c

        tag_by_name = {}
        for name in TAGS:
            t = Tag(name=name, slug=unique_slug(Tag, name))
            db.session.add(t)
            tag_by_name[name] = t

        db.session.flush()

        for item in SAMPLE_POSTS:
            cat = categories_by_slug[item["category"]]
            tag_objs = [tag_by_name[n] for n in item["tags"]]
            html_content = format_post_content(item["content"])
            post = Post(
                title=item["title"],
                slug=unique_slug(Post, item["title"]),
                content=html_content,
                excerpt=item["excerpt"][:500],
                status=item["status"],
                author_id=admin.id,
                category_id=cat.id,
                cover_image=item["cover_image"],
                views=item.get("views", 0),
            )
            post.tags = tag_objs
            db.session.add(post)

        db.session.flush()

        users = User.query.order_by(User.id.asc()).all()
        for i, seeded_user in enumerate(users):
            seeded_user.avatar = Config.AUTHOR_AVATARS[i % len(Config.AUTHOR_AVATARS)]

        db.session.commit()
        print("Seed complete (food & travel demo data).")
        print("Admin login: admin@example.com / admin123")


if __name__ == "__main__":
    seed()
