package com.csm.hybrids.client;

import com.csm.hybrids.CsmMod;
import com.csm.hybrids.client.hud.HybridHud;
import com.csm.hybrids.client.particle.CsmParticles;
import com.csm.hybrids.client.render.ChainHookRenderer;
import com.csm.hybrids.client.render.CrossbowBoltRenderer;
import com.csm.hybrids.client.render.HeadBombRenderer;
import com.csm.hybrids.client.render.HybridFormLayer;
import com.csm.hybrids.client.render.NoRenderer;
import com.csm.hybrids.client.render.SpearRenderer;
import com.csm.hybrids.registry.ModEntities;
import net.minecraft.client.renderer.entity.ThrownItemRenderer;
import net.minecraft.client.renderer.entity.player.PlayerRenderer;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.client.event.RegisterGuiOverlaysEvent;
import net.minecraftforge.client.event.RegisterKeyMappingsEvent;
import net.minecraftforge.client.event.RegisterParticleProvidersEvent;
import net.minecraftforge.client.gui.overlay.VanillaGuiOverlay;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.event.lifecycle.FMLClientSetupEvent;

@Mod.EventBusSubscriber(modid = CsmMod.MODID, bus = Mod.EventBusSubscriber.Bus.MOD, value = Dist.CLIENT)
public final class ClientModEvents {

    @SubscribeEvent
    public static void setup(FMLClientSetupEvent event) {
        event.enqueueWork(PlayerAnims::init);
    }

    @SubscribeEvent
    public static void keys(RegisterKeyMappingsEvent event) {
        event.register(Keybinds.WHEEL);
        event.register(Keybinds.USE);
        event.register(Keybinds.TRIGGER);
    }

    @SubscribeEvent
    public static void renderers(EntityRenderersEvent.RegisterRenderers event) {
        event.registerEntityRenderer(ModEntities.CHAIN_HOOK.get(), ChainHookRenderer::new);
        event.registerEntityRenderer(ModEntities.CROSSBOW_BOLT.get(), CrossbowBoltRenderer::new);
        event.registerEntityRenderer(ModEntities.NAPALM.get(), ctx -> new ThrownItemRenderer<>(ctx, 1.6f, true));
        event.registerEntityRenderer(ModEntities.SPEAR.get(), SpearRenderer::new);
        event.registerEntityRenderer(ModEntities.HEAD_BOMB.get(), HeadBombRenderer::new);
        event.registerEntityRenderer(ModEntities.SPARK_BOMB.get(), NoRenderer::new);
        event.registerEntityRenderer(ModEntities.CONTRACT_SUMMON.get(),
                com.csm.hybrids.client.render.ContractSummonRenderer::new);
        ModEntities.DEVILS.values().forEach(t -> event.registerEntityRenderer(t.get(), com.csm.hybrids.client.render.DevilRenderer::new));
    }

    @SubscribeEvent
    public static void layers(EntityRenderersEvent.AddLayers event) {
        for (String skin : event.getSkins()) {
            if (event.getSkin(skin) instanceof PlayerRenderer renderer) {
                renderer.addLayer(new HybridFormLayer(renderer, event.getContext().getItemInHandRenderer()));
            }
        }
    }

    @SubscribeEvent
    public static void particles(RegisterParticleProvidersEvent event) {
        CsmParticles.register(event);
    }

    @SubscribeEvent
    public static void overlays(RegisterGuiOverlaysEvent event) {
        event.registerAbove(VanillaGuiOverlay.HOTBAR.id(), "hybrid_hud", HybridHud::render);
        event.registerAboveAll("halloween", com.csm.hybrids.client.hud.HalloweenOverlay::render);
    }

    private ClientModEvents() {
    }
}
