package com.csm.hybrids.client.render;

import com.csm.hybrids.CsmMod;
import com.csm.hybrids.entity.ChainHookEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.Vec3;
import org.joml.Matrix3f;
import org.joml.Matrix4f;

/** Draws Denji's chain link by link from his forearm to the hook. */
public class ChainHookRenderer extends EntityRenderer<ChainHookEntity> {
    private static final ResourceLocation LINK = CsmMod.id("textures/entity/chain_link.png");
    private static final ResourceLocation HOOK = CsmMod.id("textures/entity/chain_hook.png");

    public ChainHookRenderer(EntityRendererProvider.Context ctx) {
        super(ctx);
    }

    @Override
    public void render(ChainHookEntity entity, float yaw, float partialTick, PoseStack poseStack, MultiBufferSource buffers,
                       int light) {
        Entity owner = entity.getOwner();
        if (!(owner instanceof Player player)) {
            return;
        }
        Vec3 hook = entity.getPosition(partialTick);
        Vec3 rel = handPosition(player, partialTick).subtract(hook);
        double len = rel.length();
        if (len < 0.05) {
            return;
        }
        Vec3 dir = rel.scale(1 / len);
        Vec3 side1 = dir.cross(new Vec3(0, 1, 0));
        if (side1.lengthSqr() < 1e-4) {
            side1 = new Vec3(1, 0, 0);
        }
        side1 = side1.normalize();
        Vec3 side2 = dir.cross(side1).normalize();

        poseStack.pushPose();
        Matrix4f pose = poseStack.last().pose();
        Matrix3f normal = poseStack.last().normal();
        VertexConsumer vc = buffers.getBuffer(RenderType.entityCutoutNoCull(LINK));
        double linkLen = 0.2;
        int links = Math.max(1, (int) (len / linkLen));
        for (int i = 0; i < links; i++) {
            Vec3 a = rel.scale(i / (double) links);
            Vec3 b = rel.scale((i + 1.25) / (double) links);
            Vec3 w = (i % 2 == 0 ? side1 : side2).scale(0.07);
            quad(vc, pose, normal, a, b, w, light);
        }
        VertexConsumer hc = buffers.getBuffer(RenderType.entityCutoutNoCull(HOOK));
        Vec3 tip = dir.scale(-0.35);
        Vec3 back = dir.scale(0.3);
        quad(hc, pose, normal, tip, back, side1.scale(0.2), light);
        quad(hc, pose, normal, tip, back, side2.scale(0.2), light);
        poseStack.popPose();
        super.render(entity, yaw, partialTick, poseStack, buffers, light);
    }

    private static void quad(VertexConsumer vc, Matrix4f pose, Matrix3f normal, Vec3 a, Vec3 b, Vec3 w, int light) {
        v(vc, pose, normal, a.subtract(w), 0, 0, light);
        v(vc, pose, normal, a.add(w), 1, 0, light);
        v(vc, pose, normal, b.add(w), 1, 1, light);
        v(vc, pose, normal, b.subtract(w), 0, 1, light);
    }

    private static void v(VertexConsumer vc, Matrix4f pose, Matrix3f normal, Vec3 p, float u, float v, int light) {
        vc.vertex(pose, (float) p.x, (float) p.y, (float) p.z).color(255, 255, 255, 255).uv(u, v)
                .overlayCoords(OverlayTexture.NO_OVERLAY).uv2(light).normal(normal, 0, 1, 0).endVertex();
    }

    /** Where the chain leaves Denji's right forearm. */
    static Vec3 handPosition(Player player, float partialTick) {
        Minecraft mc = Minecraft.getInstance();
        if (player == mc.player && mc.options.getCameraType().isFirstPerson()) {
            Vec3 look = player.getViewVector(partialTick);
            Vec3 right = look.cross(new Vec3(0, 1, 0)).normalize();
            return player.getEyePosition(partialTick).add(look.scale(0.5)).add(right.scale(0.32)).add(0, -0.28, 0);
        }
        float bodyYaw = Mth.lerp(partialTick, player.yBodyRotO, player.yBodyRot) * Mth.DEG_TO_RAD;
        Vec3 right = new Vec3(-Mth.cos(bodyYaw), 0, -Mth.sin(bodyYaw));
        Vec3 fwd = new Vec3(-Mth.sin(bodyYaw), 0, Mth.cos(bodyYaw));
        return player.getPosition(partialTick).add(0, 1.3, 0).add(right.scale(0.36)).add(fwd.scale(0.45));
    }

    @Override
    public ResourceLocation getTextureLocation(ChainHookEntity entity) {
        return LINK;
    }

    @Override
    public boolean shouldRender(ChainHookEntity entity, net.minecraft.client.renderer.culling.Frustum frustum, double x, double y, double z) {
        return true;
    }
}
