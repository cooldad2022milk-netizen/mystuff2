package com.csm.hybrids.registry;

import com.csm.hybrids.CsmMod;
import com.csm.hybrids.entity.ChainHookEntity;
import com.csm.hybrids.entity.CrossbowBoltEntity;
import com.csm.hybrids.entity.HeadBombEntity;
import com.csm.hybrids.entity.NapalmEntity;
import com.csm.hybrids.entity.SparkBombEntity;
import com.csm.hybrids.entity.SpearEntity;
import com.csm.hybrids.devil.DevilSpec;
import com.csm.hybrids.devil.DevilSpecs;
import com.csm.hybrids.entity.devil.DevilEntity;
import com.csm.hybrids.hybrid.HybridType;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

import java.util.EnumMap;
import java.util.HashMap;
import java.util.Map;

public final class ModEntities {
    public static final DeferredRegister<EntityType<?>> ENTITIES = DeferredRegister.create(ForgeRegistries.ENTITY_TYPES, CsmMod.MODID);

    public static final RegistryObject<EntityType<ChainHookEntity>> CHAIN_HOOK = ENTITIES.register("chain_hook",
            () -> EntityType.Builder.<ChainHookEntity>of(ChainHookEntity::new, MobCategory.MISC)
                    .sized(0.35f, 0.35f).clientTrackingRange(8).updateInterval(1).build("chain_hook"));
    public static final RegistryObject<EntityType<CrossbowBoltEntity>> CROSSBOW_BOLT = ENTITIES.register("crossbow_bolt",
            () -> EntityType.Builder.<CrossbowBoltEntity>of(CrossbowBoltEntity::new, MobCategory.MISC)
                    .sized(0.3f, 0.3f).clientTrackingRange(8).updateInterval(1).build("crossbow_bolt"));
    public static final RegistryObject<EntityType<NapalmEntity>> NAPALM = ENTITIES.register("napalm",
            () -> EntityType.Builder.<NapalmEntity>of(NapalmEntity::new, MobCategory.MISC)
                    .sized(0.5f, 0.5f).clientTrackingRange(8).updateInterval(1).fireImmune().build("napalm"));

    public static final RegistryObject<EntityType<SpearEntity>> SPEAR = ENTITIES.register("spear",
            () -> EntityType.Builder.<SpearEntity>of(SpearEntity::new, MobCategory.MISC)
                    .sized(0.4f, 0.4f).clientTrackingRange(10).updateInterval(1).build("spear"));
    public static final RegistryObject<EntityType<SparkBombEntity>> SPARK_BOMB = ENTITIES.register("spark_bomb",
            () -> EntityType.Builder.<SparkBombEntity>of(SparkBombEntity::new, MobCategory.MISC)
                    .sized(0.25f, 0.25f).clientTrackingRange(8).updateInterval(1).fireImmune().build("spark_bomb"));
    public static final RegistryObject<EntityType<HeadBombEntity>> HEAD_BOMB = ENTITIES.register("head_bomb",
            () -> EntityType.Builder.<HeadBombEntity>of(HeadBombEntity::new, MobCategory.MISC)
                    .sized(0.6f, 0.6f).clientTrackingRange(8).updateInterval(1).fireImmune().build("head_bomb"));

    // ------------------------------------------------------------------ full devils
    public static final Map<HybridType, RegistryObject<EntityType<DevilEntity>>> DEVILS = new EnumMap<>(HybridType.class);
    private static final Map<EntityType<?>, HybridType> DEVIL_OF = new HashMap<>();

    static {
        for (HybridType type : HybridType.values()) {
            if (type.devil) {
                devil(type, factoryFor(type));
            }
        }
    }

    /** Devils with rules of their own get their own class. */
    private static EntityType.EntityFactory<DevilEntity> factoryFor(HybridType type) {
        return DevilEntity::new;
    }

    /** Registry name of a devil's mob: Makima, Yoru and Fami go by their names, the rest are "<x>_devil". */
    public static String devilName(HybridType type) {
        return switch (type) {
            case CONTROL -> "makima";
            case WAR -> "yoru";
            case FAMINE -> "fami";
            case GUN_DEVIL -> "gun_devil";
            default -> type.id + "_devil";
        };
    }

    private static void devil(HybridType type, EntityType.EntityFactory<DevilEntity> factory) {
        DevilSpec s = DevilSpecs.of(type);
        String name = devilName(type);
        DEVILS.put(type, ENTITIES.register(name, () -> {
            EntityType.Builder<DevilEntity> b = EntityType.Builder.of(factory, MobCategory.MONSTER)
                    .sized(s.width, s.height).clientTrackingRange(s.boss ? 16 : 10);
            if (s.fireImmune) {
                b.fireImmune();
            }
            EntityType<DevilEntity> t = b.build(name);
            DEVIL_OF.put(t, type);
            return t;
        }));
    }

    public static HybridType devilOf(EntityType<?> type) {
        return DEVIL_OF.getOrDefault(type, HybridType.NONE);
    }

    public static EntityType<DevilEntity> devil(HybridType type) {
        return DEVILS.get(type).get();
    }

    private ModEntities() {
    }
}
