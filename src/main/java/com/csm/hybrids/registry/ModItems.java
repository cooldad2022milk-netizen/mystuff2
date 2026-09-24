package com.csm.hybrids.registry;

import com.csm.hybrids.CsmMod;
import com.csm.hybrids.hybrid.HybridType;
import com.csm.hybrids.devil.DevilSpec;
import com.csm.hybrids.devil.DevilSpecs;
import com.csm.hybrids.item.BloodVialItem;
import com.csm.hybrids.item.DevilEssenceItem;
import com.csm.hybrids.item.DevilHeartItem;
import com.csm.hybrids.item.FiendRemainsItem;
import com.csm.hybrids.item.HumanHeartItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Rarity;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.common.ForgeSpawnEggItem;
import net.minecraftforge.registries.RegistryObject;

import java.util.EnumMap;
import java.util.Map;

public final class ModItems {
    public static final DeferredRegister<Item> ITEMS = DeferredRegister.create(ForgeRegistries.ITEMS, CsmMod.MODID);

    public static final RegistryObject<Item> CHAINSAW_DEVIL_HEART = ITEMS.register("chainsaw_devil_heart",
            () -> new DevilHeartItem(HybridType.CHAINSAW, new Item.Properties().stacksTo(1).rarity(Rarity.EPIC)));
    public static final RegistryObject<Item> CROSSBOW_DEVIL_HEART = ITEMS.register("crossbow_devil_heart",
            () -> new DevilHeartItem(HybridType.CROSSBOW, new Item.Properties().stacksTo(1).rarity(Rarity.EPIC)));
    public static final RegistryObject<Item> FLAMETHROWER_DEVIL_HEART = ITEMS.register("flamethrower_devil_heart",
            () -> new DevilHeartItem(HybridType.FLAMETHROWER,
                    new Item.Properties().stacksTo(1).rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> WHIP_DEVIL_HEART = ITEMS.register("whip_devil_heart",
            () -> new DevilHeartItem(HybridType.WHIP, new Item.Properties().stacksTo(1).rarity(Rarity.EPIC)));
    public static final RegistryObject<Item> BOMB_DEVIL_HEART = ITEMS.register("bomb_devil_heart",
            () -> new DevilHeartItem(HybridType.BOMB,
                    new Item.Properties().stacksTo(1).rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryObject<Item> SPEAR_DEVIL_HEART = ITEMS.register("spear_devil_heart",
            () -> new DevilHeartItem(HybridType.SPEAR, new Item.Properties().stacksTo(1).rarity(Rarity.EPIC)));
    public static final RegistryObject<Item> KATANA_DEVIL_HEART = ITEMS.register("katana_devil_heart",
            () -> new DevilHeartItem(HybridType.KATANA, new Item.Properties().stacksTo(1).rarity(Rarity.EPIC)));
    public static final RegistryObject<Item> LONGSWORD_DEVIL_HEART = ITEMS.register("longsword_devil_heart",
            () -> new DevilHeartItem(HybridType.LONGSWORD, new Item.Properties().stacksTo(1).rarity(Rarity.EPIC)));

    public static final RegistryObject<Item> BLOOD_DEVIL_REMAINS = ITEMS.register("blood_devil_remains",
            () -> new FiendRemainsItem(HybridType.BLOOD, new Item.Properties().stacksTo(1).rarity(Rarity.EPIC)));
    public static final RegistryObject<Item> SHARK_DEVIL_REMAINS = ITEMS.register("shark_devil_remains",
            () -> new FiendRemainsItem(HybridType.SHARK, new Item.Properties().stacksTo(1).rarity(Rarity.EPIC)));
    public static final RegistryObject<Item> VIOLENCE_DEVIL_REMAINS = ITEMS.register("violence_devil_remains",
            () -> new FiendRemainsItem(HybridType.VIOLENCE, new Item.Properties().stacksTo(1).rarity(Rarity.EPIC)));
    public static final RegistryObject<Item> COSMOS_DEVIL_REMAINS = ITEMS.register("cosmos_devil_remains",
            () -> new FiendRemainsItem(HybridType.COSMOS, new Item.Properties().stacksTo(1).rarity(Rarity.EPIC)));
    public static final RegistryObject<Item> GUN_DEVIL_FLESH = ITEMS.register("gun_devil_flesh",
            () -> new FiendRemainsItem(HybridType.GUN, new Item.Properties().stacksTo(1).rarity(Rarity.EPIC)));

    public static final RegistryObject<Item> HUMAN_HEART = ITEMS.register("human_heart",
            () -> new HumanHeartItem(new Item.Properties().stacksTo(1).rarity(Rarity.UNCOMMON)));
    public static final RegistryObject<Item> BLOOD_VIAL = ITEMS.register("blood_vial",
            () -> new BloodVialItem(new Item.Properties().stacksTo(16)));

    // ------------------------------------------------------------------ full devils: essences and spawn eggs
    public static final Map<HybridType, RegistryObject<Item>> ESSENCES = new EnumMap<>(HybridType.class);
    public static final Map<HybridType, RegistryObject<Item>> SPAWN_EGGS = new EnumMap<>(HybridType.class);

    static {
        for (HybridType type : HybridType.values()) {
            if (!type.devil) {
                continue;
            }
            DevilSpec spec = DevilSpecs.of(type);
            Rarity rarity = spec.boss ? Rarity.EPIC : Rarity.RARE;
            ESSENCES.put(type, ITEMS.register(essenceName(type),
                    () -> new DevilEssenceItem(type, new Item.Properties().stacksTo(1).rarity(rarity).fireResistant())));
            SPAWN_EGGS.put(type, ITEMS.register(ModEntities.devilName(type) + "_spawn_egg",
                    () -> new ForgeSpawnEggItem(ModEntities.DEVILS.get(type), spec.eggBg, spec.eggFg, new Item.Properties())));
        }
    }

    public static String essenceName(HybridType type) {
        return (type == HybridType.GUN_DEVIL ? "gun" : type.id) + "_devil_essence";
    }

    public static Item heartFor(HybridType type) {
        return switch (type) {
            case CHAINSAW -> CHAINSAW_DEVIL_HEART.get();
            case CROSSBOW -> CROSSBOW_DEVIL_HEART.get();
            case FLAMETHROWER -> FLAMETHROWER_DEVIL_HEART.get();
            case WHIP -> WHIP_DEVIL_HEART.get();
            case BOMB -> BOMB_DEVIL_HEART.get();
            case SPEAR -> SPEAR_DEVIL_HEART.get();
            case KATANA -> KATANA_DEVIL_HEART.get();
            case LONGSWORD -> LONGSWORD_DEVIL_HEART.get();
            case BLOOD -> BLOOD_DEVIL_REMAINS.get();
            case SHARK -> SHARK_DEVIL_REMAINS.get();
            case VIOLENCE -> VIOLENCE_DEVIL_REMAINS.get();
            case COSMOS -> COSMOS_DEVIL_REMAINS.get();
            case GUN -> GUN_DEVIL_FLESH.get();
            case NONE -> HUMAN_HEART.get();
            default -> ESSENCES.get(type).get();
        };
    }

    private ModItems() {
    }
}
