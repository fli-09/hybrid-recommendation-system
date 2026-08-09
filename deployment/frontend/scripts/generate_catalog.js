import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const frontendRoot = path.resolve(path.dirname(__filename), "..");
const outputDir = path.join(frontendRoot, "src", "data");
const outputFile = path.join(outputDir, "catalog.json");

const categories = [
  {
    category: "Electronics",
    subcategories: [
      { name: "Wireless Headphones", brand: "Sony", prefix: "WH-" },
      { name: "Smart Watch", brand: "Apple", prefix: "Watch" },
      { name: "Bluetooth Speaker", brand: "JBL", prefix: "Flip" },
      { name: "Noise Cancelling Earbuds", brand: "Bose", prefix: "QuietComfort" },
      { name: "Portable Charger", brand: "Anker", prefix: "PowerCore" },
    ],
    priceRange: [79, 399],
  },
  {
    category: "Apparel",
    subcategories: [
      { name: "Running Shoes", brand: "Nike", prefix: "Air" },
      { name: "Denim Jacket", brand: "Levi's", prefix: "Trucker" },
      { name: "Outdoor Jacket", brand: "The North Face", prefix: "Ventrix" },
      { name: "Performance T-Shirt", brand: "Under Armour", prefix: "Tech" },
      { name: "Yoga Leggings", brand: "Lululemon", prefix: "Align" },
    ],
    priceRange: [29, 220],
  },
  {
    category: "Home & Kitchen",
    subcategories: [
      { name: "Air Purifier", brand: "Dyson", prefix: "Pure" },
      { name: "Espresso Machine", brand: "Breville", prefix: "Barista" },
      { name: "Robot Vacuum", brand: "iRobot", prefix: "Roomba" },
      { name: "Blender", brand: "Ninja", prefix: "Foodi" },
      { name: "Cookware Set", brand: "Lodge", prefix: "Cast-Iron" },
    ],
    priceRange: [24, 499],
  },
  {
    category: "Beauty",
    subcategories: [
      { name: "Face Serum", brand: "Olay", prefix: "Regenerist" },
      { name: "Hair Dryer", brand: "Revlon", prefix: "One-Step" },
      { name: "Makeup Palette", brand: "Urban Decay", prefix: "Naked" },
      { name: "Skin Moisturizer", brand: "Neutrogena", prefix: "Hydro Boost" },
      { name: "Perfume", brand: "Chanel", prefix: "Coco" },
    ],
    priceRange: [14, 150],
  },
  {
    category: "Sports & Outdoors",
    subcategories: [
      { name: "Camping Tent", brand: "Coleman", prefix: "Evanston" },
      { name: "Fitness Tracker", brand: "Garmin", prefix: "Forerunner" },
      { name: "Mountain Bike", brand: "Trek", prefix: "Marlin" },
      { name: "Yoga Mat", brand: "Manduka", prefix: "Pro" },
      { name: "Golf Clubs", brand: "Callaway", prefix: "Strata" },
    ],
    priceRange: [19, 999],
  },
  {
    category: "Books",
    subcategories: [
      { name: "Hardcover Bestseller", brand: "Penguin", prefix: "Modern" },
      { name: "Cookbook", brand: "Chronicle", prefix: "Home" },
      { name: "Children's Book", brand: "Scholastic", prefix: "Adventure" },
      { name: "Business Paperback", brand: "HarperCollins", prefix: "Growth" },
      { name: "Graphic Novel", brand: "Marvel", prefix: "Galaxy" },
    ],
    priceRange: [12, 45],
  },
  {
    category: "Toys",
    subcategories: [
      { name: "Building Set", brand: "LEGO", prefix: "Classic" },
      { name: "Educational Kit", brand: "Melissa & Doug", prefix: "Discovery" },
      { name: "Action Figure", brand: "Hasbro", prefix: "Transformers" },
      { name: "Board Game", brand: "Asmodee", prefix: "Ticket" },
      { name: "Remote Car", brand: "Nerf", prefix: "Volt" },
    ],
    priceRange: [15, 130],
  },
  {
    category: "Grocery",
    subcategories: [
      { name: "Organic Coffee", brand: "Lavazza", prefix: "Qualita" },
      { name: "Snack Bundle", brand: "Kind", prefix: "Nut" },
      { name: "Protein Powder", brand: "Optimum Nutrition", prefix: "Gold" },
      { name: "Olive Oil", brand: "Bertolli", prefix: "Extra" },
      { name: "Tea Collection", brand: "Twinings", prefix: "Earl" },
    ],
    priceRange: [8, 65],
  },
];

const categorySpecs = {
  Electronics: [
    ["Battery Life", "20 hours"],
    ["Connectivity", "Bluetooth 5.2"],
    ["Warranty", "2 years"],
    ["Weight", "250g"],
  ],
  Apparel: [
    ["Material", "Organic cotton blend"],
    ["Fit", "Regular"],
    ["Care", "Machine wash cold"],
    ["Sizes", "S, M, L, XL"],
  ],
  "Home & Kitchen": [
    ["Capacity", "1.5 L"],
    ["Power", "1200W"],
    ["Finish", "Stainless steel"],
    ["Dimensions", "30 x 25 x 20 cm"],
  ],
  Beauty: [
    ["Skin Type", "All skin types"],
    ["Volume", "50 mL"],
    ["Active Ingredients", "Hyaluronic acid"],
    ["Cruelty Free", "Yes"],
  ],
  "Sports & Outdoors": [
    ["Material", "Ripstop nylon"],
    ["Capacity", "4-person"],
    ["Water Resistance", "1500 mm"],
    ["Weight", "3.8 kg"],
  ],
  Books: [
    ["Pages", "320"],
    ["Language", "English"],
    ["Publisher", "Penguin Random House"],
    ["Format", "Hardcover"],
  ],
  Toys: [
    ["Recommended Age", "8+"],
    ["Piece Count", "450"],
    ["Material", "ABS plastic"],
    ["Battery", "Not required"],
  ],
  Grocery: [
    ["Net Weight", "500 g"],
    ["Ingredients", "Natural"],
    ["Shelf Life", "12 months"],
    ["Origin", "Italy"],
  ],
};

const descriptionTemplates = {
  Electronics: [
    "Powerful, polished, and built for modern life, this {brand} {prefix} {name} offers seamless performance on the go.",
    "With thoughtful engineering and sharp detail, it keeps everyday tech feeling premium and easy to use.",
    "Designed for fast connectivity and lasting comfort, this option blends innovation with a familiar user experience.",
    "A dependable choice for busy routines, it matches a sleek look with practical features customers appreciate.",
    "This product is tuned for performance, clear quality, and reliable daily use in real-world settings.",
  ],
  Apparel: [
    "Crafted for comfort and everyday movement, this piece feels as good as it looks.",
    "With premium materials and a flattering fit, it delivers style plus lasting wearability.",
    "This {brand} {prefix} {name} is made to move, breathe, and look great from morning to evening.",
    "A refined blend of durability and casual polish, it upgrades your wardrobe without overdoing it.",
    "Perfect for daily routines, it balances softness, stretch, and timeless appeal in one design.",
  ],
  "Home & Kitchen": [
    "Engineered to simplify chores and keep your space feeling fresh, this item stands out in form and function.",
    "Functional and elegant, it adds a touch of convenience to everyday home tasks with reliable performance.",
    "This product helps keep routines smooth and the kitchen looking smart, without sacrificing durability.",
    "It brings thoughtful design and easy usability to the heart of the home, where quality matters most.",
    "A valuable upgrade for daily cooking or cleaning, it pairs practical features with modern style.",
  ],
  Beauty: [
    "Lightweight, effective, and tailored to visible results, it refreshes your routine from the first use.",
    "This product puts premium skincare ingredients into a daily regimen that feels effortless and refined.",
    "With rich texture and thoughtful benefits, it keeps skin looking smoother and more vibrant day after day.",
    "Designed to soothe, protect, and enhance, it makes self-care easier without demanding extra effort.",
    "A polished formula that blends hydration and performance for everyday beauty rituals.",
  ],
  "Sports & Outdoors": [
    "Ready for the next adventure, it balances rugged reliability with a comfortable fit for active days.",
    "This gear is designed to perform in real outdoor conditions while staying lightweight and durable.",
    "Whether training or exploring, it gives you dependable support and easy motion in every setting.",
    "It blends strong construction with travel-ready style so you can focus on the activity, not the kit.",
    "Purpose-built for outdoor life, this piece helps you stay confident and comfortable during long sessions.",
  ],
  Books: [
    "A thoughtful page-turner with polished prose, it makes for a satisfying read in any setting.",
    "This selection brings sharp storytelling and strong structure to keep readers engaged from start to finish.",
    "An approachable and well-designed title that pairs compelling ideas with refined presentation.",
    "It delivers a memorable reading experience through vivid detail, strong pacing, and clear voice.",
    "A solid choice for readers who want intelligence, warmth, and a story that stays with them.",
  ],
  Toys: [
    "Bright, fun, and easy to enjoy, it encourages creative play without overcomplicating things.",
    "This set offers imaginative entertainment with sturdy pieces and thoughtful details for repeated use.",
    "Designed to inspire curiosity, it makes playtime feel lively, rewarding, and endlessly engaging.",
    "It blends quality construction with playful design so families can enjoy it again and again.",
    "A cleverly designed item that keeps kids entertained while feeling durable and well-made.",
  ],
  Grocery: [
    "Fresh flavor and premium ingredients come together in a product that fits everyday cooking easily.",
    "This choice brings quality pantry staples into meals with simple, satisfying taste and texture.",
    "Balanced and flavorful, it makes everyday dishes feel more polished without added fuss.",
    "A dependable grocery pick that adds convenience, taste, and a touch of quality to routines.",
    "This item is crafted to deliver consistent flavor and reliable performance from the first use onward.",
  ],
};

const randomFrom = (items, seed) => items[seed % items.length];
const smooth = (value) => (Math.sin(value) + 1) / 2;

function buildCatalogItem(index) {
  const catalogId = `P${String(index + 1).padStart(5, "0")}`;
  const block = categories[index % categories.length];
  const template = block.subcategories[index % block.subcategories.length];
  const rating = Number((3.2 + smooth(index * 0.37) * 1.8).toFixed(1));
  const reviewCount = Math.max(5, Math.round(15 + smooth(index * 0.53) * 49985));
  const basePrice = block.priceRange[0] + ((index * 17) % (block.priceRange[1] - block.priceRange[0] + 1));
  const price = Number((basePrice + ((index % 7) * 4.5)).toFixed(2));
  const stockRoll = index % 20;
  const stockStatus = stockRoll === 0 ? "out_of_stock" : stockRoll <= 2 ? "low_stock" : "in_stock";
  const title = `${template.brand} ${template.prefix} ${template.name}`;
  const descriptionTemplate = randomFrom(descriptionTemplates[block.category] || descriptionTemplates.Electronics, index);
  const description = descriptionTemplate
    .replace(/{brand}/g, template.brand)
    .replace(/{prefix}/g, template.prefix)
    .replace(/{name}/g, template.name);
  const images = [
    `/images/products/${catalogId}_1.svg`,
    `/images/products/${catalogId}_2.svg`,
  ];

  const specs = Object.fromEntries(
    categorySpecs[block.category].map(([key, value], idx) => {
      const valueSuffix = idx % 2 === 0 ? value : value;
      return [key, valueSuffix];
    })
  );

  return {
    catalogId,
    title,
    brand: template.brand,
    category: block.category,
    subcategory: template.name,
    price,
    currency: "USD",
    rating,
    reviewCount,
    stockStatus,
    specifications: specs,
    description,
    images,
  };
}

function generateCatalog(count = 800) {
  return Array.from({ length: count }, (_, index) => buildCatalogItem(index));
}

function ensureDir(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

function main() {
  ensureDir(outputDir);
  const catalog = generateCatalog(800);
  fs.writeFileSync(outputFile, JSON.stringify(catalog, null, 2), "utf-8");
  console.log(`Generated catalog with ${catalog.length} products at ${outputFile}`);
}

main();
