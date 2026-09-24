package com.csm.hybrids.registry;

import com.csm.hybrids.CsmMod;
import com.csm.hybrids.loot.DevilHeartLootModifier;
import com.mojang.serialization.Codec;
import net.minecraftforge.common.loot.IGlobalLootModifier;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public final class ModLootModifiers {
    public static final DeferredRegister<Codec<? extends IGlobalLootModifier>> SERIALIZERS =
            DeferredRegister.create(ForgeRegistries.Keys.GLOBAL_LOOT_MODIFIER_SERIALIZERS, CsmMod.MODID);

    public static final RegistryObject<Codec<DevilHeartLootModifier>> DEVIL_HEART =
            SERIALIZERS.register("devil_heart_loot", DevilHeartLootModifier.CODEC);

    private ModLootModifiers() {
    }
}
