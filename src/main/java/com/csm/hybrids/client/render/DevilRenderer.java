package com.csm.hybrids.client.render;

import com.csm.hybrids.CsmMod;
import com.csm.hybrids.devil.DevilSpec;
import com.csm.hybrids.entity.devil.DevilEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.resources.ResourceLocation;
import org.jetbrains.annotations.Nullable;
import software.bernie.geckolib.cache.object.BakedGeoModel;
import software.bernie.geckolib.cache.object.GeoBone;
import software.bernie.geckolib.model.GeoModel;
import software.bernie.geckolib.renderer.GeoEntityRenderer;
import software.bernie.geckolib.renderer.layer.AutoGlowingGeoLayer;

import java.util.Arrays;

/**
 * Renders every full devil (mob or a player's devil form) from assets/csm/{geo,textures,animations}/entity/devil/.
 * <p>
 * Bone name prefixes: fx_&lt;group&gt;_ bones only show while that effect group is active (a move's props: Makima's
 * chains, the Angel's lifespan weapons...). In the first-person view of a player's own form, the bones listed in
 * {@link DevilSpec#firstPersonHidden} are hidden so the camera is not buried inside the devil's head.
 */
public class DevilRenderer extends GeoEntityRenderer<DevilEntity> {
    /** Set while drawing the local player's own form from the first-person camera. */
    public static boolean firstPersonPass;

    public DevilRenderer(EntityRendererProvider.Context ctx) {
        super(ctx, new Model());
        addRenderLayer(new AutoGlowingGeoLayer<>(this));
    }

    @Override
    public void preRender(PoseStack poseStack, DevilEntity devil, BakedGeoModel model, MultiBufferSource bufferSource,
                          VertexConsumer buffer, boolean isReRender, float partialTick, int packedLight, int packedOverlay,
                          float red, float green, float blue, float alpha) {
        DevilSpec spec = devil.spec();
        float s = devil.isPuppet() ? spec.playerScale() : 1f;
        this.scaleWidth = s;
        this.scaleHeight = s;
        this.shadowRadius = spec.shadow * s;
        if (!isReRender) {
            String[] hidden = firstPersonPass ? spec.firstPersonHidden : new String[0];
            for (GeoBone bone : model.topLevelBones()) {
                applyVisibility(devil, bone, hidden);
            }
        }
        super.preRender(poseStack, devil, model, bufferSource, buffer, isReRender, partialTick, packedLight, packedOverlay,
                red, green, blue, alpha);
    }

    private void applyVisibility(DevilEntity devil, GeoBone bone, String[] hidden) {
        String n = bone.getName();
        boolean visible = true;
        if (n.startsWith("fx_")) {
            int end = n.indexOf('_', 3);
            visible = end > 3 && devil.fxActive(n.substring(3, end));
        }
        if (visible && hidden.length > 0 && Arrays.asList(hidden).contains(n)) {
            visible = false;
        }
        bone.setHidden(!visible);
        if (visible) {
            for (GeoBone child : bone.getChildBones()) {
                applyVisibility(devil, child, hidden);
            }
        }
    }

    /** Ghostly devils are drawn see-through. */
    @Override
    public software.bernie.geckolib.core.object.Color getRenderColor(DevilEntity devil, float partialTick,
                                                                   int packedLight) {
        if (devil.spec().translucent) {
            return software.bernie.geckolib.core.object.Color.ofRGBA(255, 255, 255, firstPersonPass ? 90 : 115);
        }
        return super.getRenderColor(devil, partialTick, packedLight);
    }

    @Override
    public RenderType getRenderType(DevilEntity devil, ResourceLocation texture, @Nullable MultiBufferSource bufferSource,
                                    float partialTick) {
        return devil.spec().translucent ? RenderType.entityTranslucent(texture) : RenderType.entityCutoutNoCull(texture);
    }

    @Override
    protected float getDeathMaxRotation(DevilEntity devil) {
        return 0f; // devils play their own death animation instead of tipping over
    }

    @Override
    public boolean shouldShowName(DevilEntity devil) {
        return !devil.isPuppet() && super.shouldShowName(devil);
    }

    static class Model extends GeoModel<DevilEntity> {
        @Override
        public ResourceLocation getModelResource(DevilEntity devil) {
            return CsmMod.id("geo/entity/devil/" + devil.devilType().id + ".geo.json");
        }

        @Override
        public ResourceLocation getTextureResource(DevilEntity devil) {
            return CsmMod.id("textures/entity/devil/" + devil.devilType().id + ".png");
        }

        @Override
        public ResourceLocation getAnimationResource(DevilEntity devil) {
            return CsmMod.id("animations/entity/devil/" + devil.devilType().id + ".animation.json");
        }
    }
}
