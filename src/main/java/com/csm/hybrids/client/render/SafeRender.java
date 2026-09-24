package com.csm.hybrids.client.render;

import com.csm.hybrids.util.Safe;
import com.mojang.blaze3d.vertex.PoseStack;

/**
 * Draws through {@link Safe}: a model that fails to draw (a broken or missing model or animation file) is skipped and
 * logged once, instead of crashing the game. The pose stack is put back how it was.
 */
public final class SafeRender {
    public static void draw(String what, PoseStack poseStack, Runnable draw) {
        PoseStack.Pose before = poseStack.last();
        try {
            draw.run();
        } catch (RuntimeException | LinkageError e) {
            Safe.report(what, e);
            while (poseStack.last() != before && !poseStack.clear()) {
                poseStack.popPose();
            }
        }
    }

    private SafeRender() {
    }
}
