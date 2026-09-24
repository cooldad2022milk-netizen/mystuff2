package com.csm.hybrids.client.render;

import com.csm.hybrids.CsmMod;
import com.csm.hybrids.entity.HeadBombEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.model.GeoModel;
import software.bernie.geckolib.renderer.GeoEntityRenderer;
import software.bernie.geckolib.renderer.layer.AutoGlowingGeoLayer;

/** Reze's thrown bomb head, tumbling end over end with its fuse lit. Uses the Bomb hybrid's texture atlas. */
public class HeadBombRenderer extends GeoEntityRenderer<HeadBombEntity> {
    public HeadBombRenderer(EntityRendererProvider.Context ctx) {
        super(ctx, new Model());
        addRenderLayer(new AutoGlowingGeoLayer<>(this));
    }

    @Override
    public void render(HeadBombEntity entity, float entityYaw, float partialTick, PoseStack poseStack,
                       net.minecraft.client.renderer.MultiBufferSource bufferSource, int packedLight) {
        SafeRender.draw("head bomb model", poseStack,
                () -> super.render(entity, entityYaw, partialTick, poseStack, bufferSource, packedLight));
    }

    @Override
    protected void applyRotations(HeadBombEntity bomb, PoseStack poseStack, float ageInTicks, float rotationYaw,
                                  float partialTick) {
        poseStack.translate(0, 0.3, 0);
        poseStack.mulPose(Axis.YP.rotationDegrees(-bomb.getYRot()));
        poseStack.mulPose(Axis.XP.rotationDegrees((bomb.tickCount + partialTick) * 24f));
        poseStack.translate(0, -0.3, 0);
    }

    static class Model extends GeoModel<HeadBombEntity> {
        @Override
        public ResourceLocation getModelResource(HeadBombEntity animatable) {
            return CsmMod.id("geo/entity/bomb_head.geo.json");
        }

        @Override
        public ResourceLocation getTextureResource(HeadBombEntity animatable) {
            return CsmMod.id("textures/hybrid/bomb.png");
        }

        @Override
        public ResourceLocation getAnimationResource(HeadBombEntity animatable) {
            return CsmMod.id("animations/entity/bomb_head.animation.json");
        }
    }
}
