package com.csm.hybrids.client.render;

import com.csm.hybrids.CsmMod;
import com.csm.hybrids.entity.CrossbowBoltEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.math.Axis;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import software.bernie.geckolib.cache.object.BakedGeoModel;
import software.bernie.geckolib.model.GeoModel;
import software.bernie.geckolib.renderer.GeoEntityRenderer;
import software.bernie.geckolib.renderer.layer.AutoGlowingGeoLayer;

/** GeckoLib bolt, pointed along its flight path. The overdrawn piercing bolt is bigger and glows. */
public class CrossbowBoltRenderer extends GeoEntityRenderer<CrossbowBoltEntity> {
    public CrossbowBoltRenderer(EntityRendererProvider.Context ctx) {
        super(ctx, new Model());
        addRenderLayer(new AutoGlowingGeoLayer<>(this));
    }

    @Override
    public void render(CrossbowBoltEntity entity, float entityYaw, float partialTick, PoseStack poseStack,
                       MultiBufferSource bufferSource, int packedLight) {
        SafeRender.draw("crossbow bolt model", poseStack,
                () -> super.render(entity, entityYaw, partialTick, poseStack, bufferSource, packedLight));
    }

    @Override
    protected void applyRotations(CrossbowBoltEntity bolt, PoseStack poseStack, float ageInTicks, float rotationYaw,
                                  float partialTick) {
        poseStack.mulPose(Axis.YP.rotationDegrees(Mth.lerp(partialTick, bolt.yRotO, bolt.getYRot()) + 180f));
        poseStack.mulPose(Axis.XP.rotationDegrees(Mth.lerp(partialTick, bolt.xRotO, bolt.getXRot())));
    }

    @Override
    public void preRender(PoseStack poseStack, CrossbowBoltEntity bolt, BakedGeoModel model, MultiBufferSource bufferSource,
                          VertexConsumer buffer, boolean isReRender, float partialTick, int packedLight, int packedOverlay,
                          float red, float green, float blue, float alpha) {
        super.preRender(poseStack, bolt, model, bufferSource, buffer, isReRender, partialTick, packedLight, packedOverlay,
                red, green, blue, alpha);
        if (!isReRender) {
            model.getBone("glow").ifPresent(b -> b.setHidden(!bolt.isPiercing()));
            if (bolt.isPiercing()) {
                poseStack.scale(2.2f, 2.2f, 2.2f);
            }
        }
    }

    static class Model extends GeoModel<CrossbowBoltEntity> {
        @Override
        public ResourceLocation getModelResource(CrossbowBoltEntity animatable) {
            return CsmMod.id("geo/entity/crossbow_bolt.geo.json");
        }

        @Override
        public ResourceLocation getTextureResource(CrossbowBoltEntity animatable) {
            return CsmMod.id("textures/entity/crossbow_bolt.png");
        }

        @Override
        public ResourceLocation getAnimationResource(CrossbowBoltEntity animatable) {
            return CsmMod.id("animations/entity/crossbow_bolt.animation.json");
        }
    }
}
