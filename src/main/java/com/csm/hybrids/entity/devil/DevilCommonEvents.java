package com.csm.hybrids.entity.devil;

import com.csm.hybrids.CsmMod;
import com.csm.hybrids.devil.DevilSpecs;
import com.csm.hybrids.registry.ModEntities;
import net.minecraftforge.event.entity.EntityAttributeCreationEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Mod-bus registration for the devil mobs: their attributes. */
@Mod.EventBusSubscriber(modid = CsmMod.MODID, bus = Mod.EventBusSubscriber.Bus.MOD)
public final class DevilCommonEvents {

    @SubscribeEvent
    public static void attributes(EntityAttributeCreationEvent event) {
        ModEntities.DEVILS.forEach((type, entity) ->
                event.put(entity.get(), DevilEntity.attributes(DevilSpecs.of(type)).build()));
    }

    private DevilCommonEvents() {
    }
}
