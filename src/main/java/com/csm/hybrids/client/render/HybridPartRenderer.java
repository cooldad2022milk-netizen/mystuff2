package com.csm.hybrids.client.render;

import com.csm.hybrids.CsmMod;
import com.csm.hybrids.client.ClientHybridState;
import com.csm.hybrids.hybrid.HybridType;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.model.PlayerModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.player.AbstractClientPlayer;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.LivingEntityRenderer;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;
import org.jetbrains.annotations.Nullable;
import org.joml.Matrix4f;
import org.joml.Vector3f;
import org.joml.Vector4f;
import software.bernie.geckolib.cache.object.BakedGeoModel;
import software.bernie.geckolib.cache.object.GeoBone;
import software.bernie.geckolib.renderer.GeoObjectRenderer;
import software.bernie.geckolib.renderer.layer.AutoGlowingGeoLayer;

/**
 * Renders a hybrid's devil parts glued onto the (PlayerAnimator-animated) vanilla player model.
 * <p>
 * Every top-level bone of the geo model is named after a vanilla part (head, body, right_arm, ...).
 * Instead of GeckoLib's own root transform, each such bone is placed with the matching
 * {@link ModelPart#translateAndRotate} so the devil parts follow walking, swinging and every body animation.
 * Bedrock -> model space is a 180 degree roll ({@code scale(-1,-1,1)}) plus moving the bone pivot to the origin.
 * <p>
 * Bone name prefixes drive visibility: form_ (devil form out), human_ (human form, hidden once the trigger
 * starts), prop_ (anything worn while human, e.g. Reze's choker or Galgali's mask), base_ (always: a fiend's
 * horns, shark head, exposed brain...), trig_ (held during the trigger),
 * fx_&lt;group&gt;_ (ability effects such as leg saws or flame jets).
 * <p>
 * One bone per hybrid can be carried in the right fist during the trigger (the chainsaw starter handle, the
 * grenade pin): see {@link #computeHandleTarget}.
 */
public class HybridPartRenderer extends GeoObjectRenderer<HybridPartsAnimatable> {
    private static final ResourceLocation CORD_TEXTURE = CsmMod.id("textures/hybrid/cord.png");
    private static HybridPartRenderer instance;

    private PlayerModel<?> parts;
    private ClientHybridState state;
    private AbstractClientPlayer player;
    private double now;
    private String onlyPart;
    private boolean firstPersonPass;
    private Matrix4f basePose;
    private Vector3f handleTarget;
    private String followBone = "";
    private Vector3f cordStart;
    private Vector3f cordEnd;

    public HybridPartRenderer() {
        super(new HybridPartsModel());
        // emissive parts: chainsaw vent-slit eyes, crossbow overcharge, flamethrower pilot lights and flame jets
        addRenderLayer(new AutoGlowingGeoLayer<>(this));
    }

    public static HybridPartRenderer get() {
        if (instance == null) {
            instance = new HybridPartRenderer();
        }
        return instance;
    }

    /**
     * @param onlyPart when non-null only that top-level bone is drawn (first-person arm rendering)
     */
    public void renderOnPlayer(PoseStack poseStack, MultiBufferSource buffers, int light, AbstractClientPlayer player,
                               PlayerModel<?> model, ClientHybridState state, float partialTick, boolean firstPersonPass,
                               @Nullable String onlyPart) {
        if (state.type == HybridType.NONE) {
            return;
        }
        this.parts = model;
        this.state = state;
        this.player = player;
        this.now = ClientHybridState.now(partialTick);
        this.onlyPart = onlyPart;
        this.firstPersonPass = firstPersonPass;
        this.basePose = new Matrix4f(poseStack.last().pose());
        this.cordStart = null;
        this.cordEnd = null;
        state.renderNow = this.now;
        this.handleTarget = computeHandleTarget(model);
        try {
            SafeRender.draw("hybrid model " + state.type.id, poseStack, () -> {
                render(poseStack, state.animatable(), buffers, null, null, light);
                if (cordStart != null && cordEnd != null && onlyPart == null && !firstPersonPass) {
                    drawCord(buffers.getBuffer(RenderType.entityCutoutNoCull(CORD_TEXTURE)), cordStart, cordEnd, light);
                }
            });
        } finally {
            this.parts = null;
            this.player = null;
            this.state = null;
        }
    }

    @Override
    public long getInstanceId(HybridPartsAnimatable animatable) {
        return animatable.instanceId;
    }

    @Override
    public int getPackedOverlay(HybridPartsAnimatable animatable, float u) {
        return player != null ? LivingEntityRenderer.getOverlayCoords(player, u) : OverlayTexture.NO_OVERLAY;
    }

    @Override
    public int getPackedOverlay(HybridPartsAnimatable animatable, float u, float partialTick) {
        return getPackedOverlay(animatable, u);
    }

    @Override
    public void preRender(PoseStack poseStack, HybridPartsAnimatable animatable, BakedGeoModel model,
                          MultiBufferSource bufferSource, VertexConsumer buffer, boolean isReRender, float partialTick,
                          int packedLight, int packedOverlay, float red, float green, float blue, float alpha) {
        // no block-centering offset: the vanilla model parts position everything
        this.objectRenderTranslations = new Matrix4f(poseStack.last().pose());
        if (!isReRender && state != null) {
            for (GeoBone bone : model.topLevelBones()) {
                applyVisibility(bone);
            }
        }
    }

    private void applyVisibility(GeoBone bone) {
        String n = bone.getName();
        boolean visible = true;
        String exclusive = state.exclusiveFx(now);
        if (exclusive != null && bone.getParent() != null && !n.startsWith("fx_" + exclusive)) {
            // the whole body has become something else (Beam's full shark form)
            bone.setHidden(true);
            return;
        }
        boolean form = state.formVisible(now);
        double trig = state.triggerSeconds(now);
        if (n.startsWith("form_")) {
            visible = form;
        } else if (n.startsWith("human_")) {
            visible = !form && trig < 0.15;
        } else if (n.startsWith("prop_")) {
            visible = !form;
        } else if (n.startsWith("base_")) {
            visible = true;
        } else if (n.startsWith("trig_")) {
            visible = trig >= 0.15 && trig < 1.2;
        } else if (n.startsWith("fx_")) {
            int end = n.indexOf('_', 3);
            visible = end > 3 && state.fxActive(n.substring(3, end), now);
        }
        bone.setHidden(!visible);
        if (visible) {
            for (GeoBone child : bone.getChildBones()) {
                applyVisibility(child);
            }
        }
    }

    @Override
    public void renderRecursively(PoseStack poseStack, HybridPartsAnimatable animatable, GeoBone bone, RenderType renderType,
                                  MultiBufferSource bufferSource, VertexConsumer buffer, boolean isReRender, float partialTick,
                                  int packedLight, int packedOverlay, float red, float green, float blue, float alpha) {
        if (bone.getParent() == null) {
            ModelPart part = partFor(bone.getName());
            if (part == null || !partAllowed(bone.getName())) {
                return;
            }
            poseStack.pushPose();
            part.translateAndRotate(poseStack);
            poseStack.scale(-1, -1, 1);
            poseStack.translate(-bone.getPivotX() / 16f, -bone.getPivotY() / 16f, -bone.getPivotZ() / 16f);
            super.renderRecursively(poseStack, animatable, bone, renderType, bufferSource, buffer, isReRender, partialTick,
                    packedLight, packedOverlay, red, green, blue, alpha);
            poseStack.popPose();
            return;
        }
        String name = bone.getName();
        if ("cord".equals(name) && !isReRender) {
            cordStart = poseStack.last().pose().transformPosition(pivotOf(bone));
        }
        if (name.equals(followBone)) {
            Vector3f pivot = pivotOf(bone);
            if (handleTarget != null) {
                // the prop is in the fist: move it to the hand, keep the body's orientation
                Vector3f targetView = basePose.transformPosition(new Vector3f(handleTarget));
                Vector3f local = new Matrix4f(poseStack.last().pose()).invert().transformPosition(new Vector3f(targetView));
                poseStack.pushPose();
                poseStack.translate(local.x - pivot.x, local.y - pivot.y, local.z - pivot.z);
                if (!isReRender) {
                    cordEnd = targetView;
                }
                super.renderRecursively(poseStack, animatable, bone, renderType, bufferSource, buffer, isReRender,
                        partialTick, packedLight, packedOverlay, red, green, blue, alpha);
                poseStack.popPose();
                return;
            }
            if (!isReRender) {
                cordEnd = poseStack.last().pose().transformPosition(new Vector3f(pivot));
            }
        }
        super.renderRecursively(poseStack, animatable, bone, renderType, bufferSource, buffer, isReRender, partialTick,
                packedLight, packedOverlay, red, green, blue, alpha);
    }

    private static Vector3f pivotOf(GeoBone bone) {
        return new Vector3f(bone.getPivotX() / 16f, bone.getPivotY() / 16f, bone.getPivotZ() / 16f);
    }

    @Nullable
    private ModelPart partFor(String name) {
        return switch (name) {
            case "head" -> parts.head;
            case "body" -> parts.body;
            case "right_arm" -> parts.rightArm;
            case "left_arm" -> parts.leftArm;
            case "right_leg" -> parts.rightLeg;
            case "left_leg" -> parts.leftLeg;
            default -> null;
        };
    }

    private boolean partAllowed(String name) {
        if (onlyPart != null) {
            return onlyPart.equals(name);
        }
        return !firstPersonPass || name.endsWith("_arm");
    }

    /**
     * Chainsaw trigger choreography (seconds): 0.12-0.25 the handle is drawn out to meet the hand, 0.25-0.62 it
     * is held while the cord is yanked, 0.62-0.74 it snaps back into the chest.
     * <p>
     * Bomb: the fingers hook the pin ring under the choker at 0.38-0.44 and it stays in the fist from then on.
     */
    @Nullable
    private Vector3f computeHandleTarget(PlayerModel<?> model) {
        double t = state.triggerSeconds(now);
        if (state.type == HybridType.BOMB) {
            followBone = "trig_pin";
            if (t < 0.38) {
                return null;
            }
            Vector3f hand = partPoint(model.rightArm, -1f, 10.6f, -0.6f);
            Vector3f neck = partPoint(model.head, 0f, 0.7f, -4.42f);
            return t < 0.44 ? neck.lerp(hand, smooth((float) ((t - 0.38) / 0.06))) : hand;
        }
        if (state.type != HybridType.CHAINSAW) {
            followBone = "";
            return null;
        }
        followBone = "cord_handle";
        if (t < 0.12 || t > 0.74) {
            return null;
        }
        Vector3f hand = partPoint(model.rightArm, -1f, 10.4f, 0f);
        Vector3f rest = partPoint(model.body, 0f, 3.5f, -3.6f);
        if (t < 0.25) {
            return rest.lerp(hand, smooth((float) ((t - 0.12) / 0.13)));
        }
        if (t < 0.62) {
            return hand;
        }
        return hand.lerp(rest, smooth((float) ((t - 0.62) / 0.12)));
    }

    private static float smooth(float x) {
        x = Math.max(0, Math.min(1, x));
        return x * x * (3 - 2 * x);
    }

    /** A point given in a vanilla part's local pixel coordinates, in model space (blocks). */
    private static Vector3f partPoint(ModelPart part, float x, float y, float z) {
        PoseStack ps = new PoseStack();
        part.translateAndRotate(ps);
        Vector4f v = ps.last().pose().transform(new Vector4f(x / 16f, y / 16f, z / 16f, 1f));
        return new Vector3f(v.x, v.y, v.z);
    }

    /** Pochita's starter cord: a rubber cord from the chest to the handle (wherever the hand has pulled it). */
    private static void drawCord(VertexConsumer vc, Vector3f a, Vector3f b, int light) {
        Vector3f d = new Vector3f(b).sub(a);
        if (d.lengthSquared() < 1e-6f) {
            return;
        }
        Vector3f n1 = new Vector3f(d).cross(0, 1, 0);
        if (n1.lengthSquared() < 1e-6f) {
            n1.set(1, 0, 0);
        }
        n1.normalize(0.022f);
        Vector3f n2 = new Vector3f(d).cross(n1).normalize(0.022f);
        float len = d.length();
        quad(vc, a, b, n1, len, light);
        quad(vc, a, b, n2, len, light);
    }

    private static void quad(VertexConsumer vc, Vector3f a, Vector3f b, Vector3f n, float len, int light) {
        float v1 = Math.min(1f, len * 2f);
        vertex(vc, a.x - n.x, a.y - n.y, a.z - n.z, 0f, 0f, light);
        vertex(vc, a.x + n.x, a.y + n.y, a.z + n.z, 1f, 0f, light);
        vertex(vc, b.x + n.x, b.y + n.y, b.z + n.z, 1f, v1, light);
        vertex(vc, b.x - n.x, b.y - n.y, b.z - n.z, 0f, v1, light);
    }

    private static void vertex(VertexConsumer vc, float x, float y, float z, float u, float v, int light) {
        vc.vertex(x, y, z).color(255, 255, 255, 255).uv(u, v).overlayCoords(OverlayTexture.NO_OVERLAY).uv2(light)
                .normal(0, 1, 0).endVertex();
    }
}
