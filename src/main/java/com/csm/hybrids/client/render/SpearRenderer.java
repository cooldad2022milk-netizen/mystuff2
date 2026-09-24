package com.csm.hybrids.client.render;

import com.csm.hybrids.CsmMod;
import com.csm.hybrids.entity.SpearEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import software.bernie.geckolib.model.GeoModel;
import software.bernie.geckolib.renderer.GeoEntityRenderer;

/**
 * The Spear Hybrid's spears. Thrown ones point along their flight path; erupting ones stand up out of the ground
 * (the "rise" animation pushes them up from below).
 */
public class SpearRenderer extends GeoEntityRenderer<SpearEntity> {
    public SpearRenderer(EntityRendererProvider.Context ctx) {
        super(ctx, new Model());
    }

    @Override
    public void render(SpearEntity entity, float entityYaw, float partialTick, PoseStack poseStack,
                       net.minecraft.client.renderer.MultiBufferSource bufferSource, int packedLight) {
        SafeRender.draw("spear model", poseStack,
                () -> super.render(entity, entityYaw, partialTick, poseStack, bufferSource, packedLight));
    }

    @Override
    protected void applyRotations(SpearEntity spear, PoseStack poseStack, float ageInTicks, float rotationYaw,
                                  float partialTick) {
        float s = spear.scale();
        if (spear.mode() == SpearEntity.ERUPT) {
            poseStack.mulPose(Axis.YP.rotationDegrees(spear.getYRot()));
            poseStack.mulPose(Axis.XP.rotationDegrees(90f + spear.getXRot()));
        } else {
            poseStack.mulPose(Axis.YP.rotationDegrees(Mth.lerp(partialTick, spear.yRotO, spear.getYRot()) + 180f));
            poseStack.mulPose(Axis.XP.rotationDegrees(Mth.lerp(partialTick, spear.xRotO, spear.getXRot())));
        }
        poseStack.scale(s, s, s);
    }

    static class Model extends GeoModel<SpearEntity> {
        @Override
        public ResourceLocation getModelResource(SpearEntity animatable) {
            return CsmMod.id(animatable.variant() == SpearEntity.BLOOD ? "geo/entity/blood_spear.geo.json"
                    : "geo/entity/spear.geo.json");
        }

        @Override
        public ResourceLocation getTextureResource(SpearEntity animatable) {
            return CsmMod.id(animatable.variant() == SpearEntity.BLOOD ? "textures/entity/blood_spear.png"
                    : "textures/entity/spear.png");
        }

        @Override
        public ResourceLocation getAnimationResource(SpearEntity animatable) {
            return CsmMod.id("animations/entity/spear.animation.json");
        }
    }
}
