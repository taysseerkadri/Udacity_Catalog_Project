from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from model import Base, Brand, BrandAddress, ClothingItem

engine = create_engine('sqlite:///clothing.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

brand1 = Brand(name="Adidas",
               picture="http://www.thelogofactory.com/wp-content/uploads/2015/09/adidas-logo.png",
               description="Adidas AG is a German multinational corporation, headquartered in Herzogenaurach, Bavaria, that designs and manufactures shoes, clothing and accessories. It is the largest sportswear manufacturer in Europe, and the second largest in the world.")
brand1Address = BrandAddress(streetaddress="adidas AG Adi-Dassler-Strasse 1", city="Herzogenaurach",
                             state="", postalcode="91074", country="Germany", brand=brand1)
clothingItem1_1 = ClothingItem(name="MEN'S MESSI 16+ PUREAGILITY FIRM GROUND SHOES",
                             picture="http://www.adidas.ca/dis/dw/image/v2/aaqx_prd/on/demandware.static/-/Sites-adidas-products/default/dwc60406cf/zoom/BA9821_01_standard.jpg?sw=500&sfrm=jpg",
                             description="Colour Copper Metallic/Core Black/Solar Green",
                             price=199.95,
                             stockamount=12,
                             brand=brand1)
clothingItem1_2 = ClothingItem(name="MEN'S PADDED BACK-TO-SCHOOL 3-STRIPES JACKET",
                             picture="http://www.adidas.ca/dis/dw/image/v2/aaqx_prd/on/demandware.static/-/Sites-adidas-products/default/dw4f6df8bc/zoom/BP9412_21_model.jpg?sw=500&sfrm=jpg",
                             description="Colour Black/White (BP9412)",
                             price=200.00,
                             stockamount=25,
                             brand=brand1)
clothingItem1_3 = ClothingItem(name="WOMEN'S YOGA SEAMLESS TANK TOP",
                             picture="http://www.adidas.ca/dis/dw/image/v2/aaqx_prd/on/demandware.static/-/Sites-adidas-products/default/dweeafdb6b/zoom/S97511_21_model.jpg?sw=500&sfrm=jpg",
                             description="Colour Wonder Glow/White (S97511)",
                             price=99.95,
                             stockamount=18,
                             brand=brand1)
session.add(brand1)
session.add(brand1Address)
session.add(clothingItem1_1)
session.add(clothingItem1_2)
session.add(clothingItem1_3)
session.commit()

brand2 = Brand(name="Nike",
               picture="http://static2.businessinsider.com/image/53d29d5c6bb3f7a80617ada8-480/nike-logo.png",
               description="Nike, Inc. is an American multinational corporation that is engaged in the design, development, manufacturing, and worldwide marketing and sales of footwear, apparel, equipment, accessories, and services.")
brand2Address = BrandAddress(streetaddress="Nike World Headquarters - One Bowerman Drive",
                             city="Beaverton",
                             state="OR",
                             postalcode="97005",
                             country="USA",
                             brand=brand2)
clothingItem2_1 = ClothingItem(name="NIKE AIR MAX INFURIATE LOW",
                             picture="https://images.nike.com/is/image/DotCom/PDP_HERO_M/852457_101_A_PREM/air-max-infuriate-low-mens-basketball-shoe.jpg",
                             description="Black/White/Dark Grey/Black - Style: 852457-010",
                             price=105.00,
                             stockamount=5,
                             brand=brand2)
clothingItem2_2 = ClothingItem(name="TORONTO RAPTORS NIKE",
                             picture="https://images.nike.com/is/image/DotCom/PDP_HERO_M/881167_010_A/toronto-raptors-fleece-nba-hoodie.jpg",
                             description="Colour Black/Black Style: 881167-010",
                             price=80.00,
                             stockamount=20,
                             brand=brand2)
clothingItem2_3 = ClothingItem(name="HURLEY BOUQUET",
                             picture="https://www.swiminn.com/f/13645/136459405_5/hurley-bouquet.jpg",
                             description="Colour Black/White Style: AH0406-011",
                             price=68.00,
                             stockamount=28,
                             brand=brand2)
session.add(brand2)
session.add(brand2Address)
session.add(clothingItem2_1)
session.add(clothingItem2_2)
session.add(clothingItem2_3)
session.commit()

brand3 = Brand(name="New Balance",
               picture="https://s-media-cache-ak0.pinimg.com/originals/2a/79/4d/2a794de25a58f36afd25883502c930e8.jpg",
               description='New Balance Athletics, Inc. (NB), best known as simply New Balance, is an American multinational corporation based in the Brighton neighborhood of Boston, Massachusetts. The company was founded in 1906 as the "New Balance Arch Support Company" and is one of the world\'s major sports footwear manufacturers.')
brand3Address = BrandAddress(streetaddress="New Balance Corp Headquarters - 140 Guest St",
                             city="Brighton",
                             state="MA",
                             postalcode="02135",
                             country="USA",
                             brand=brand3)
clothingItem3_1 = ClothingItem(name="Fresh Foam Zante v3",
                             picture="http://nb.scene7.com/is/image/NB/mzantwg3_nb_02_i?$dw_temp_default_gallery$",
                             description="Color: Arctic Fox with Black & White",
                             price=99.99,
                             stockamount=11,
                             brand=brand3)
clothingItem3_2 = ClothingItem(name="Essentials Full Zip Hoodie",
                             picture="http://nb.scene7.com/is/image/NB/mj73528ag_nb_40_i?$dw_temp_default_gallery$",
                             description="Color: Athletic Grey",
                             price=74.99,
                             stockamount=32,
                             brand=brand3)
clothingItem3_3 = ClothingItem(name="Short Sleeve Graphic T-Shirt",
                             picture="http://nb.scene7.com/is/image/NB/gt12574aga_nb_40_i?$dw_temp_default_gallery$",
                             description="Color: Agave",
                             price=15.99,
                             stockamount=56,
                             brand=brand3)
session.add(brand3)
session.add(brand3Address)
session.add(clothingItem3_1)
session.add(clothingItem3_2)
session.add(clothingItem3_3)
session.commit()


print "added menu items!"
