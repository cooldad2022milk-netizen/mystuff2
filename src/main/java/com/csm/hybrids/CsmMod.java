package com.csm.hybrids;

import com.csm.hybrids.config.CsmConfig;
import com.csm.hybrids.hybrid.HybridCapability;
import com.csm.hybrids.network.CsmNetwork;
import com.csm.hybrids.registry.ModEntities;
import com.csm.hybrids.registry.ModItems;
import com.csm.hybrids.registry.ModLootModifiers;
import com.csm.hybrids.registry.ModParticles;
import com.csm.hybrids.registry.ModSounds;
import com.csm.hybrids.registry.ModTabs;
import com.mojang.logging.LogUtils;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.ModLoadingContext;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.config.ModConfig;
import net.minecraftforge.fml.event.lifecycle.FMLCommonSetupEvent;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import org.slf4j.Logger;

/**
 * Chainsaw Man: Hybrids.
 * <p>
 * Players become devil hybrids by ripping out their own heart and replacing it with a devil's heart
 * (Chainsaw, Crossbow or Flamethrower). Each hybrid has a manga-accurate trigger that transforms them
 * and a set of abilities picked from the ability wheel (V).
 */
@Mod(CsmMod.MODID)
public class CsmMod {
    public static final String MODID = "csm";
    public static final Logger LOGGER = LogUtils.getLogger();

    @SuppressWarnings("removal") // keeps working on every 47.x Forge build
    public CsmMod() {
        IEventBus bus = FMLJavaModLoadingContext.get().getModEventBus();
        ModItems.ITEMS.register(bus);
        ModSounds.SOUNDS.register(bus);
        ModParticles.PARTICLES.register(bus);
        com.csm.hybrids.registry.ModEffects.EFFECTS.register(bus);
        ModEntities.ENTITIES.register(bus);
        ModTabs.TABS.register(bus);
        ModLootModifiers.SERIALIZERS.register(bus);
        bus.addListener(this::commonSetup);
        bus.addListener(HybridCapability::register);
        ModLoadingContext.get().registerConfig(ModConfig.Type.COMMON, CsmConfig.SPEC);
    }

    private void commonSetup(FMLCommonSetupEvent event) {
        event.enqueueWork(CsmNetwork::register);
    }

    @SuppressWarnings("removal")
    public static ResourceLocation id(String path) {
        return new ResourceLocation(MODID, path);
    }
}
