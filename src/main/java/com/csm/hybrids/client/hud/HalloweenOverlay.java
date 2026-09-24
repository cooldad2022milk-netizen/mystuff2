package com.csm.hybrids.client.hud;

import com.csm.hybrids.registry.ModEffects;
import com.mojang.blaze3d.systems.RenderSystem;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraftforge.client.gui.overlay.ForgeGui;

/**
 * What it is like to be hit by Cosmo: the whole universe floods in at once. Stars close in from the edges of the screen
 * and "Halloween" fills your head, more and more of it.
 */
public final class HalloweenOverlay {

    public static void render(ForgeGui gui, GuiGraphics g, float partialTick, int width, int height) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.player == null || mc.options.hideGui) {
            return;
        }
        MobEffectInstance fx = mc.player.getEffect(ModEffects.HALLOWEEN.get());
        if (fx == null) {
            return;
        }
        float t = mc.player.tickCount + partialTick;
        float strength = Mth.clamp(fx.getDuration() / 40f, 0f, 1f) * Mth.clamp((t % 100000) / 10f, 0f, 1f);
        RenderSystem.enableBlend();
        // the cosmos pressing in from the edges
        int layers = 12;
        for (int i = 0; i < layers; i++) {
            float f = i / (float) layers;
            int inset = (int) (f * Math.min(width, height) * 0.45f);
            int a = (int) (strength * 18 * (1 - f));
            int col = (a << 24) | 0x20062E;
            g.fill(0, 0, width, inset, col);
            g.fill(0, height - inset, width, height, col);
            g.fill(0, inset, inset, height - inset, col);
            g.fill(width - inset, inset, width, height - inset, col);
        }
        // stars
        RandomSource r = RandomSource.create(1234L);
        for (int i = 0; i < 140; i++) {
            float x = r.nextFloat() * width;
            float y = r.nextFloat() * height;
            float dx = x - width / 2f;
            float dy = y - height / 2f;
            float edge = Mth.clamp((Math.abs(dx) / (width / 2f) + Math.abs(dy) / (height / 2f)) - 0.6f, 0f, 1f);
            float tw = 0.5f + 0.5f * Mth.sin(t * 0.25f + i);
            int a = (int) (255 * strength * edge * tw);
            if (a < 8) {
                continue;
            }
            int c = (i % 3 == 0) ? 0xFFB0E0 : (i % 3 == 1 ? 0xC8B8FF : 0xFFF2C8);
            int s = 1 + (i % 4 == 0 ? 1 : 0);
            g.fill((int) x, (int) y, (int) x + s, (int) y + s, (a << 24) | c);
        }
        // "Halloween", more and more of it
        int words = (int) (4 + 14 * strength);
        for (int i = 0; i < words; i++) {
            float x = r.nextFloat() * (width - 60) + 10 + Mth.sin(t * 0.05f + i) * 6;
            float y = r.nextFloat() * (height - 20) + 5 + Mth.cos(t * 0.04f + i * 1.7f) * 4;
            float scale = 0.8f + r.nextFloat() * 1.6f;
            int a = (int) (strength * (110 + 110 * (0.5f + 0.5f * Mth.sin(t * 0.18f + i * 2.1f))));
            g.pose().pushPose();
            g.pose().translate(x, y, 0);
            g.pose().scale(scale, scale, 1);
            g.drawString(mc.font, "Halloween", 0, 0, (Math.max(a, 8) << 24) | 0xFF9ACD, false);
            g.pose().popPose();
        }
        RenderSystem.disableBlend();
    }

    private HalloweenOverlay() {
    }
}
