package com.csm.hybrids.client;

import com.csm.hybrids.CsmMod;
import com.csm.hybrids.client.render.DevilRenderer;
import com.csm.hybrids.client.render.HybridPartRenderer;
import com.csm.hybrids.entity.devil.DevilEntity;
import com.csm.hybrids.client.screen.AbilityWheelScreen;
import com.csm.hybrids.client.sound.EngineSound;
import com.csm.hybrids.hybrid.HybridCapability;
import com.csm.hybrids.hybrid.HybridData;
import com.csm.hybrids.hybrid.HybridType;
import com.csm.hybrids.network.CsmNetwork;
import com.csm.hybrids.network.UseAbilityPacket;
import net.minecraft.ChatFormatting;
import net.minecraft.client.Minecraft;
import net.minecraft.client.model.PlayerModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.player.AbstractClientPlayer;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.player.PlayerRenderer;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.HumanoidArm;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.Vec3;
import net.minecraft.util.Mth;
import com.csm.hybrids.registry.ModParticles;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RenderArmEvent;
import net.minecraftforge.client.event.RenderHandEvent;
import net.minecraftforge.client.event.RenderLevelStageEvent;
import net.minecraftforge.client.event.RenderPlayerEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = CsmMod.MODID, bus = Mod.EventBusSubscriber.Bus.FORGE, value = Dist.CLIENT)
public final class ClientForgeEvents {

    @SubscribeEvent
    public static void clientTick(TickEvent.ClientTickEvent event) {
        if (event.phase != TickEvent.Phase.END) {
            return;
        }
        Minecraft mc = Minecraft.getInstance();
        if (mc.player == null || mc.level == null) {
            return;
        }
        HybridData data = HybridCapability.get(mc.player);
        while (Keybinds.WHEEL.consumeClick()) {
            if (data != null && data.hasAbilities()) {
                if (mc.screen == null) {
                    mc.setScreen(new AbilityWheelScreen(data));
                }
            } else {
                mc.player.displayClientMessage(Component.translatable("msg.csm.not_hybrid").withStyle(ChatFormatting.GRAY), true);
            }
        }
        while (Keybinds.USE.consumeClick()) {
            if (data != null && data.hasAbilities()) {
                CsmNetwork.toServer(new UseAbilityPacket(data.selected()));
            }
        }
        while (Keybinds.TRIGGER.consumeClick()) {
            if (data != null && data.isHybrid()) {
                CsmNetwork.toServer(new UseAbilityPacket(0));
            }
        }
        // chainsaw engines + ambient devil effects
        double now = ClientHybridState.now(0);
        for (Player p : mc.level.players()) {
            ClientHybridState st = ClientHybridState.of(p);
            if (st == null || !st.transformed) {
                continue;
            }
            boolean firstPersonSelf = p == mc.player && mc.options.getCameraType().isFirstPerson();
            if (st.type == HybridType.CHAINSAW) {
                if (!(st.engineSound instanceof EngineSound s) || s.isStopped()) {
                    EngineSound sound = new EngineSound(p, st);
                    st.engineSound = sound;
                    mc.getSoundManager().play(sound);
                }
                boolean rev = st.revving(now);
                float yaw = p.getYHeadRot() * Mth.DEG_TO_RAD;
                Vec3 left = new Vec3(Mth.cos(yaw), 0, Mth.sin(yaw));
                Vec3 look = new Vec3(-Mth.sin(yaw), 0, Mth.cos(yaw));
                if (!firstPersonSelf && p.tickCount % (rev ? 1 : 5) == 0) {
                    // two-stroke exhaust out of the muffler on the left of the skull
                    Vec3 m = p.getEyePosition().add(left.scale(0.33)).add(look.scale(-0.12)).add(0, -0.08, 0);
                    mc.level.addParticle(ModParticles.EXHAUST.get(), m.x, m.y, m.z, left.x * 0.07, 0.03, left.z * 0.07);
                }
                if (rev && p.tickCount % 2 == 0) {
                    // in your own first-person view sparks that close to the eye would fill the screen
                    Vec3 tip = p.getEyePosition().add(p.getViewVector(1f).scale(firstPersonSelf ? 2.4 : 1.1));
                    mc.level.addParticle(ModParticles.SPARK.get(), tip.x, tip.y, tip.z,
                            (p.getRandom().nextDouble() - 0.5) * 0.3, 0.1 + p.getRandom().nextDouble() * 0.15,
                            (p.getRandom().nextDouble() - 0.5) * 0.3);
                }
            } else if (st.type == HybridType.CHAINSAW_DEVIL) {
                // Pochita's engine never stops while it is out
                if (!(st.engineSound instanceof EngineSound s) || s.isStopped()) {
                    EngineSound sound = new EngineSound(p, st);
                    st.engineSound = sound;
                    mc.getSoundManager().play(sound);
                }
                if (!firstPersonSelf && p.tickCount % (st.revving(now) ? 2 : 6) == 0) {
                    Vec3 m = p.position().add(0, p.getBbHeight() * 0.95, 0);
                    mc.level.addParticle(ModParticles.EXHAUST.get(), m.x, m.y, m.z, 0, 0.06, 0);
                }
            } else if (st.type == HybridType.FLAMETHROWER && p.tickCount % 6 == 0) {
                // pilot lights drip embers under the nozzles
                float by = p.yBodyRot * Mth.DEG_TO_RAD;
                Vec3 right = new Vec3(-Mth.cos(by), 0, -Mth.sin(by));
                for (int side = -1; side <= 1; side += 2) {
                    Vec3 n = p.position().add(right.scale(0.38 * side)).add(0, 0.12, 0);
                    mc.level.addParticle(ModParticles.EMBER.get(), n.x, n.y, n.z, 0, 0.02, 0);
                }
            } else if (st.type == HybridType.BOMB && p.tickCount % 3 == 0) {
                // the lit wicks of the fuses wound round her forearms sputter
                float by = p.yBodyRot * Mth.DEG_TO_RAD;
                Vec3 right = new Vec3(-Mth.cos(by), 0, -Mth.sin(by));
                int side = (p.tickCount / 3) % 2 == 0 ? 1 : -1;
                Vec3 n = p.position().add(right.scale(0.42 * side)).add(0, 0.78, 0);
                mc.level.addParticle(ModParticles.SPARK.get(), n.x, n.y, n.z, (p.getRandom().nextDouble() - 0.5) * 0.12,
                        0.06 + p.getRandom().nextDouble() * 0.08, (p.getRandom().nextDouble() - 0.5) * 0.12);
                if (p.tickCount % 12 == 0) {
                    mc.level.addParticle(ModParticles.EMBER.get(), n.x, n.y, n.z, 0, 0.02, 0);
                }
            }
        }
    }

    /**
     * Hide the vanilla head (and arms, for hybrids whose arms become weapons) where the devil parts replace them,
     * grow Galgali when unmasked and sink Beam into the ground while he swims through it.
     */
    @SubscribeEvent
    public static void renderPlayer(RenderPlayerEvent.Pre event) {
        if (!(event.getEntity() instanceof AbstractClientPlayer player)) {
            return;
        }
        ClientHybridState st = ClientHybridState.of(player);
        if (st == null || st.type == HybridType.NONE) {
            return;
        }
        double now = ClientHybridState.now(event.getPartialTick());
        boolean form = st.formVisible(now);
        if (form && st.type.monster()) {
            // the player IS the devil now: draw its model instead of the body
            DevilEntity puppet = st.puppet(player);
            if (puppet != null) {
                event.setCanceled(true);
                st.renderNow = now;
                st.syncPuppet(puppet, player);
                Minecraft.getInstance().getEntityRenderDispatcher().getRenderer(puppet).render(puppet,
                        Mth.lerp(event.getPartialTick(), player.yRotO, player.getYRot()), event.getPartialTick(),
                        event.getPoseStack(), event.getMultiBufferSource(), event.getPackedLight());
            }
            return;
        }
        PlayerModel<AbstractClientPlayer> model = event.getRenderer().getModel();
        if (st.exclusiveFx(now) != null) {
            // the whole body is a shark now
            model.setAllVisible(false);
        }
        if (form ? st.type.formHidesHead : st.type.baseHidesHead) {
            model.head.visible = false;
            model.hat.visible = false;
        }
        if (form && st.type.replacesArms) {
            model.rightArm.visible = false;
            model.leftArm.visible = false;
            model.rightSleeve.visible = false;
            model.leftSleeve.visible = false;
        }
        float scale = st.renderScale(now);
        double sink = st.sink(now);
        if (scale != 1f || sink != 0) {
            event.getPoseStack().pushPose();
            event.getPoseStack().translate(0, -sink, 0);
            event.getPoseStack().scale(scale, scale, scale);
            SCALED.add(player.getId());
        }
    }

    private static final java.util.Set<Integer> SCALED = new java.util.HashSet<>();

    @SubscribeEvent
    public static void renderPlayerPost(RenderPlayerEvent.Post event) {
        if (SCALED.remove(event.getEntity().getId())) {
            event.getPoseStack().popPose();
        }
    }

    /** First person: draw the devil forearm (and hide the human one when the arm is replaced). */
    @SubscribeEvent
    public static void renderArm(RenderArmEvent event) {
        AbstractClientPlayer player = event.getPlayer();
        ClientHybridState st = ClientHybridState.of(player);
        if (st == null || st.type == HybridType.NONE) {
            return;
        }
        double now = ClientHybridState.now(Minecraft.getInstance().getFrameTime());
        boolean form = st.formVisible(now);
        boolean trig = st.triggerSeconds(now) >= 0;
        if (st.type.monster()) {
            if (form) {
                event.setCanceled(true); // the devil's own body is drawn in the world instead
            }
            return;
        }
        if (st.exclusiveFx(now) != null) {
            event.setCanceled(true); // no hands in shark form
            return;
        }
        if (!form && !trig && !st.type.fiend) {
            return;
        }
        EntityRenderer<? super AbstractClientPlayer> r = Minecraft.getInstance().getEntityRenderDispatcher().getRenderer(player);
        if (!(r instanceof PlayerRenderer renderer)) {
            return;
        }
        PlayerModel<AbstractClientPlayer> model = renderer.getModel();
        HumanoidArm arm = event.getArm();
        model.attackTime = 0f;
        model.crouching = false;
        model.swimAmount = 0f;
        model.setupAnim(player, 0f, 0f, 0f, 0f, 0f);
        ModelPart part = arm == HumanoidArm.RIGHT ? model.rightArm : model.leftArm;
        part.xRot = 0f;
        if (form && st.type.replacesArms) {
            event.setCanceled(true);
        }
        HybridPartRenderer.get().renderOnPlayer(event.getPoseStack(), event.getMultiBufferSource(), event.getPackedLight(),
                player, model, st, Minecraft.getInstance().getFrameTime(), false,
                arm == HumanoidArm.RIGHT ? "right_arm" : "left_arm");
    }

    /** No floating human hand (or held item) in front of a devil's face. */
    @SubscribeEvent
    public static void renderHand(RenderHandEvent event) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.player == null) {
            return;
        }
        ClientHybridState st = ClientHybridState.of(mc.player);
        if (st != null && st.type.monster() && st.formVisible(ClientHybridState.now(event.getPartialTick()))) {
            event.setCanceled(true);
        }
    }

    /**
     * First person in a monster devil's form: the vanilla renderer never draws the camera's own entity, so draw the
     * devil's body in the world ourselves (minus its head, which would sit on the camera). Looking down you see your
     * devil body; claws, wings and jaws swing into view during moves.
     */
    @SubscribeEvent
    public static void renderOwnDevil(RenderLevelStageEvent event) {
        if (event.getStage() != RenderLevelStageEvent.Stage.AFTER_ENTITIES) {
            return;
        }
        Minecraft mc = Minecraft.getInstance();
        if (mc.player == null || !mc.options.getCameraType().isFirstPerson() || mc.player.isSpectator()) {
            return;
        }
        AbstractClientPlayer player = mc.player;
        ClientHybridState st = ClientHybridState.of(player);
        float pt = event.getPartialTick();
        double now = ClientHybridState.now(pt);
        if (st == null || !st.type.monster() || !st.formVisible(now)) {
            return;
        }
        DevilEntity puppet = st.puppet(player);
        if (puppet == null) {
            return;
        }
        st.renderNow = now;
        st.syncPuppet(puppet, player);
        Vec3 cam = event.getCamera().getPosition();
        com.mojang.blaze3d.vertex.PoseStack ps = event.getPoseStack();
        ps.pushPose();
        ps.translate(Mth.lerp(pt, player.xo, player.getX()) - cam.x, Mth.lerp(pt, player.yo, player.getY()) - cam.y,
                Mth.lerp(pt, player.zo, player.getZ()) - cam.z);
        net.minecraft.client.renderer.MultiBufferSource.BufferSource buffers = mc.renderBuffers().bufferSource();
        DevilRenderer.firstPersonPass = true;
        try {
            mc.getEntityRenderDispatcher().getRenderer(puppet).render(puppet, Mth.lerp(pt, player.yRotO, player.getYRot()),
                    pt, ps, buffers, mc.getEntityRenderDispatcher().getPackedLightCoords(player, pt));
        } finally {
            DevilRenderer.firstPersonPass = false;
        }
        buffers.endBatch();
        ps.popPose();
    }

    private ClientForgeEvents() {
    }
}
