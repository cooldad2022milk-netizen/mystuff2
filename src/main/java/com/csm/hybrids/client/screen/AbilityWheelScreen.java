package com.csm.hybrids.client.screen;

import com.csm.hybrids.ability.Ability;
import com.csm.hybrids.client.Keybinds;
import com.csm.hybrids.hybrid.HybridCapability;
import com.csm.hybrids.hybrid.HybridData;
import com.csm.hybrids.hybrid.HybridType;
import com.csm.hybrids.network.CsmNetwork;
import com.csm.hybrids.network.SelectAbilityPacket;
import com.mojang.blaze3d.platform.InputConstants;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.BufferBuilder;
import com.mojang.blaze3d.vertex.BufferUploader;
import com.mojang.blaze3d.vertex.DefaultVertexFormat;
import com.mojang.blaze3d.vertex.Tesselator;
import com.mojang.blaze3d.vertex.VertexFormat;
import net.minecraft.ChatFormatting;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.renderer.GameRenderer;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.util.FormattedCharSequence;
import net.minecraft.util.Mth;
import org.joml.Matrix4f;
import org.lwjgl.glfw.GLFW;

import java.util.List;

/**
 * Radial ability wheel. Hold V, point at a move and release to select it (or tap V to keep the wheel open and
 * click). Number keys pick slots directly. The selected move is then performed with the Use Ability key.
 */
public class AbilityWheelScreen extends Screen {
    private static final float OUTER = 112f;
    private static final float INNER = 46f;

    private final HybridType type;
    private final List<Ability> abilities;
    private final long openedAt = System.currentTimeMillis();
    private boolean holdMode = true;
    private int hovered = -1;
    private float appear;

    public AbilityWheelScreen(HybridData data) {
        this(data, true);
    }

    /** @param holdMode true when opened by holding the wheel key (release selects). */
    public AbilityWheelScreen(HybridData data, boolean holdMode) {
        super(Component.translatable("screen.csm.ability_wheel"));
        this.type = data.type();
        this.abilities = data.abilities();
        this.holdMode = holdMode;
    }

    @Override
    public boolean isPauseScreen() {
        return false;
    }

    @Override
    public void tick() {
        InputConstants.Key key = Keybinds.WHEEL.getKey();
        if (holdMode && key.getType() == InputConstants.Type.KEYSYM) {
            boolean down = InputConstants.isKeyDown(Minecraft.getInstance().getWindow().getWindow(), key.getValue());
            if (!down) {
                if (System.currentTimeMillis() - openedAt < 220) {
                    holdMode = false; // quick tap: keep the wheel open until a click
                } else {
                    confirm(hovered);
                }
            }
        }
    }

    private void confirm(int index) {
        if (index >= 0 && index < abilities.size()) {
            HybridData data = HybridCapability.get(Minecraft.getInstance().player);
            if (data != null) {
                data.setSelected(index);
            }
            CsmNetwork.toServer(new SelectAbilityPacket(index));
            Minecraft.getInstance().getSoundManager().play(SimpleSoundInstance.forUI(SoundEvents.UI_BUTTON_CLICK.value(), 1.4f, 0.6f));
        }
        onClose();
    }

    @Override
    public boolean mouseClicked(double mouseX, double mouseY, int button) {
        if (button == GLFW.GLFW_MOUSE_BUTTON_LEFT) {
            confirm(hovered);
            return true;
        }
        if (button == GLFW.GLFW_MOUSE_BUTTON_RIGHT) {
            onClose();
            return true;
        }
        return super.mouseClicked(mouseX, mouseY, button);
    }

    @Override
    public boolean keyPressed(int keyCode, int scanCode, int modifiers) {
        if (keyCode >= GLFW.GLFW_KEY_1 && keyCode <= GLFW.GLFW_KEY_9) {
            confirm(keyCode - GLFW.GLFW_KEY_1);
            return true;
        }
        if (!holdMode && Keybinds.WHEEL.matches(keyCode, scanCode)) {
            confirm(hovered);
            return true;
        }
        return super.keyPressed(keyCode, scanCode, modifiers);
    }

    @Override
    public void render(GuiGraphics g, int mouseX, int mouseY, float partialTick) {
        Minecraft mc = Minecraft.getInstance();
        HybridData data = HybridCapability.get(mc.player);
        if (data == null || abilities.isEmpty()) {
            onClose();
            return;
        }
        appear = Math.min(1f, appear + partialTick * 0.35f + 0.08f);
        float ease = 1f - (1f - appear) * (1f - appear);
        g.fillGradient(0, 0, width, height, 0x90100000, 0xC0000000);

        float cx = width / 2f;
        float cy = height / 2f;
        // shrink the wheel on small windows / large GUI scales so labels stay on screen
        float fit = Math.min(1f, Math.min(width / 2f - 10f, height / 2f - 34f) / (OUTER + 8f));
        float outer = OUTER * fit * (0.8f + 0.2f * ease);
        float inner = INNER * fit * (0.8f + 0.2f * ease);
        int n = abilities.size();
        float slice = 360f / n;

        double dx = mouseX - cx;
        double dy = mouseY - cy;
        double dist = Math.sqrt(dx * dx + dy * dy);
        if (dist > inner * 0.55) {
            double ang = Math.toDegrees(Math.atan2(dy, dx)) + 90 + slice / 2;
            ang = ((ang % 360) + 360) % 360;
            hovered = Mth.clamp((int) (ang / slice), 0, n - 1);
        } else {
            hovered = -1;
        }

        g.flush();
        for (int i = 0; i < n; i++) {
            int base = abilities.get(i).wheelColor();
            float a0 = -90 - slice / 2 + i * slice + 1.2f;
            float a1 = a0 + slice - 2.4f;
            boolean hot = i == hovered;
            boolean chosen = i == data.selected();
            int fill = hot ? argb(0xE0, base) : (chosen ? 0xD0401010 : 0xB0101014);
            float grow = hot ? 6f : 0f;
            ring(g, cx, cy, inner, outer + grow, a0, a1, fill, hot ? argb(0xFF, brighten(base)) : 0xC0200808);
            ring(g, cx, cy, outer + grow - 2.5f, outer + grow, a0, a1, chosen ? 0xFFFF3030 : 0x80FFFFFF, 0);
        }
        ring(g, cx, cy, inner - 6, inner - 2, 0, 360, 0xC0801010, 0);

        for (int i = 0; i < n; i++) {
            Ability ab = abilities.get(i);
            float mid = (float) Math.toRadians(-90 + i * slice);
            float r = (inner + outer) / 2f + (i == hovered ? 3 : 0);
            int ix = Math.round(cx + Mth.cos(mid) * r);
            int iy = Math.round(cy + Mth.sin(mid) * r);
            int size = (i == hovered ? 30 : 26) - (n > 16 ? 6 : 0);
            boolean usable = !ab.requiresForm() || data.isTransformed();
            if (!usable) {
                RenderSystem.setShaderColor(0.45f, 0.45f, 0.45f, 1f);
            }
            g.blit(ab.icon(), ix - size / 2, iy - size / 2 - 4, size, size, 0, 0, 32, 32, 32, 32);
            RenderSystem.setShaderColor(1f, 1f, 1f, 1f);
            int cd = data.cooldown(i);
            if (cd > 0) {
                int max = Math.max(1, data.cooldownMax(i));
                int h = Math.round(size * cd / (float) max);
                g.fill(ix - size / 2, iy - size / 2 - 4 + (size - h), ix + size / 2, iy + size / 2 - 4, 0xA0000000);
                g.drawCenteredString(font, String.format("%.1f", cd / 20f), ix, iy - 8, 0xFFFFFFFF);
            }
            g.drawCenteredString(font, String.valueOf(i + 1), ix, iy + size / 2 - 1, 0xFFB0B0B0);
        }

        // centre panel: name, description, cost
        // a plain human with contracts is a devil hunter; anyone else is what lives in them
        Component title = type == HybridType.NONE ? Component.translatable("screen.csm.contractor") : type.displayName();
        int titleColor = type == HybridType.NONE ? abilities.get(0).wheelColor() : type.color;
        g.drawCenteredString(font, title.copy().withStyle(ChatFormatting.BOLD), (int) cx, (int) (cy - outer - 22),
                titleColor);
        if (data.isHybrid()) {
            g.drawCenteredString(font, Component.translatable("screen.csm.blood", (int) data.blood()), (int) cx,
                    (int) (cy - outer - 11), 0xFFD02020);
        } else {
            g.drawCenteredString(font, Component.translatable("screen.csm.contracts", data.contracts().size()),
                    (int) cx, (int) (cy - outer - 11), 0xFFB0A090);
        }
        int show = hovered >= 0 ? hovered : data.selected();
        if (show >= 0 && show < n) {
            Ability ab = abilities.get(show);
            Component name = ab.isTrigger() && data.isTransformed()
                    ? Component.translatable("ability.csm.revert") : ab.displayName();
            g.drawCenteredString(font, name.copy().withStyle(ChatFormatting.BOLD), (int) cx, (int) cy - 16, 0xFFFFFFFF);
            // wide enough for the longer descriptions, and always ending above the key hint at the bottom
            int wrap = (int) Math.max(inner * 1.7f, Math.min(width - 40, 340));
            List<FormattedCharSequence> lines = font.split(ab.description(), wrap);
            int y = (int) Math.min(cy + outer + 14, height - 26 - lines.size() * 10);
            int boxW = 0;
            for (FormattedCharSequence line : lines) {
                boxW = Math.max(boxW, font.width(line));
            }
            g.fill((int) (cx - boxW / 2f) - 4, y - 3, (int) (cx + boxW / 2f) + 4, y + lines.size() * 10 + 1, 0x90000000);
            for (FormattedCharSequence line : lines) {
                g.drawString(font, line, (int) (cx - font.width(line) / 2f), y, 0xFFDDDDDD);
                y += 10;
            }
            String cost = ab.price() != null ? ab.price().getString()
                    : ab.bloodCost() > 0 ? Component.translatable("screen.csm.cost", (int) ab.bloodCost()).getString() : "";
            g.drawCenteredString(font, cost, (int) cx, (int) cy - 4, 0xFFFF5555);
            g.drawCenteredString(font, Component.translatable("screen.csm.cooldown",
                    String.format("%.1f", ab.cooldown() / 20f)), (int) cx, (int) cy + 6, 0xFFAAAAAA);
            if (ab.requiresForm() && !data.isTransformed()) {
                g.drawCenteredString(font, Component.translatable("screen.csm.needs_form"), (int) cx, (int) cy + 17, 0xFFFF8040);
            }
        }
        g.drawCenteredString(font, Component.translatable(holdMode ? "screen.csm.hint_hold" : "screen.csm.hint_click",
                Keybinds.USE.getTranslatedKeyMessage()), (int) cx, height - 20, 0xFF909090);
    }

    private static int argb(int alpha, int rgb) {
        return (alpha << 24) | (rgb & 0xFFFFFF);
    }

    private static int brighten(int rgb) {
        int r = Math.min(255, ((rgb >> 16) & 0xFF) + 60);
        int gr = Math.min(255, ((rgb >> 8) & 0xFF) + 60);
        int b = Math.min(255, (rgb & 0xFF) + 60);
        return (r << 16) | (gr << 8) | b;
    }

    /** Filled annulus slice between angles a0..a1 (degrees, 0 = +x, clockwise on screen). */
    private static void ring(GuiGraphics g, float cx, float cy, float r0, float r1, float a0, float a1, int colorIn, int colorOut) {
        if (colorOut == 0) {
            colorOut = colorIn;
        }
        Matrix4f m = g.pose().last().pose();
        RenderSystem.enableBlend();
        RenderSystem.defaultBlendFunc();
        RenderSystem.setShader(GameRenderer::getPositionColorShader);
        BufferBuilder bb = Tesselator.getInstance().getBuilder();
        bb.begin(VertexFormat.Mode.TRIANGLE_STRIP, DefaultVertexFormat.POSITION_COLOR);
        int steps = Math.max(6, (int) ((a1 - a0) / 3f));
        for (int i = 0; i <= steps; i++) {
            float a = (float) Math.toRadians(a0 + (a1 - a0) * i / steps);
            float cos = Mth.cos(a);
            float sin = Mth.sin(a);
            bb.vertex(m, cx + cos * r1, cy + sin * r1, 0).color(colorOut >> 16 & 0xFF, colorOut >> 8 & 0xFF,
                    colorOut & 0xFF, colorOut >>> 24).endVertex();
            bb.vertex(m, cx + cos * r0, cy + sin * r0, 0).color(colorIn >> 16 & 0xFF, colorIn >> 8 & 0xFF,
                    colorIn & 0xFF, colorIn >>> 24).endVertex();
        }
        BufferUploader.drawWithShader(bb.end());
        RenderSystem.disableBlend();
    }
}
