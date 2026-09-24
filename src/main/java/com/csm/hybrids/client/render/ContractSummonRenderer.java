package com.csm.hybrids.client.render;

import com.csm.hybrids.CsmMod;
import com.csm.hybrids.entity.ContractSummonEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import org.jetbrains.annotations.Nullable;
import software.bernie.geckolib.core.object.Color;
import software.bernie.geckolib.model.GeoModel;
import software.bernie.geckolib.renderer.GeoEntityRenderer;
import software.bernie.geckolib.renderer.layer.AutoGlowingGeoLayer;

/**
 * Draws a contract devil's summoned part from assets/csm/{geo,textures,animations}/entity/contract/&lt;model&gt;. The
 * Ghost Devil's arm is invisible to everyone but its contractor, who sees it pale and see-through; anyone else only
 * catches a shimmer.
 */
public class ContractSummonRenderer extends GeoEntityRenderer<ContractSummonEntity> {
    public ContractSummonRenderer(EntityRendererProvider.Context ctx) {
        super(ctx, new Model());
        addRenderLayer(new AutoGlowingGeoLayer<>(this));
        this.shadowRadius = 0f;
    }

    @Override
    public void render(ContractSummonEntity summon, float entityYaw, float partialTick, PoseStack poseStack,
                       MultiBufferSource bufferSource, int packedLight) {
        SafeRender.draw("contract model " + summon.kind().model, poseStack,
                () -> super.render(summon, entityYaw, partialTick, poseStack, bufferSource, packedLight));
    }

    /** Not a living thing: turn it by its own yaw (its front faces the way it attacks). */
    @Override
    protected void applyRotations(ContractSummonEntity summon, PoseStack poseStack, float ageInTicks, float rotationYaw,
                                  float partialTick) {
        poseStack.mulPose(Axis.YP.rotationDegrees(180f - Mth.rotLerp(partialTick, summon.yRotO, summon.getYRot())));
    }

    @Override
    public Color getRenderColor(ContractSummonEntity summon, float partialTick, int packedLight) {
        if (summon.kind().ghostly) {
            Minecraft mc = Minecraft.getInstance();
            boolean mine = mc.player != null && mc.player.getId() == summon.ownerId();
            return Color.ofRGBA(255, 255, 255, mine ? 150 : 18);
        }
        return super.getRenderColor(summon, partialTick, packedLight);
    }

    @Override
    public RenderType getRenderType(ContractSummonEntity summon, ResourceLocation texture,
                                    @Nullable MultiBufferSource bufferSource, float partialTick) {
        return summon.kind().ghostly ? RenderType.entityTranslucent(texture) : RenderType.entityCutoutNoCull(texture);
    }

    static class Model extends GeoModel<ContractSummonEntity> {
        @Override
        public ResourceLocation getModelResource(ContractSummonEntity summon) {
            return CsmMod.id("geo/entity/contract/" + summon.kind().model + ".geo.json");
        }

        @Override
        public ResourceLocation getTextureResource(ContractSummonEntity summon) {
            return CsmMod.id("textures/entity/contract/" + summon.kind().model + ".png");
        }

        @Override
        public ResourceLocation getAnimationResource(ContractSummonEntity summon) {
            return CsmMod.id("animations/entity/contract/" + summon.kind().model + ".animation.json");
        }
    }
}
