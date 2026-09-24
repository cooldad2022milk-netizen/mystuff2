package com.csm.hybrids.client.hud;

import com.csm.hybrids.ability.Ability;
import com.csm.hybrids.client.Keybinds;
import com.csm.hybrids.hybrid.HybridCapability;
import com.csm.hybrids.hybrid.HybridData;
import net.minecraft.ChatFormatting;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.network.chat.Component;
import net.minecraftforge.client.gui.overlay.ForgeGui;

import java.util.List;

/** Blood gauge + currently selected ability, left of the hotbar. */
public final class HybridHud {

    public static void render(ForgeGui gui, GuiGraphics g, float partialTick, int width, int height) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.player == null || mc.options.hideGui || mc.player.isSpectator()) {
            return;
        }
        HybridData data = HybridCapability.get(mc.player);
        if (data == null || !data.isHybrid()) {
            return;
        }
        List<Ability> abilities = data.type().abilities();
        if (abilities.isEmpty()) {
            return;
        }
        Font font = mc.font;
        int panel = 124;
        int x = width / 2 - 91 - panel - 6;
        int y = height - 30;
        if (x < 4) {       // narrow screens / big GUI scale: sit above the left end of the hotbar
            x = 4;
            y = height - 82;
        }
        int ix = x;
        int iy = y;
        int tx = x + 30;
        int barW = 90;

        // blood gauge
        float blood = data.blood() / HybridData.MAX_BLOOD;
        g.fill(tx - 1, iy + 19, tx + barW + 1, iy + 26, 0xFF000000);
        g.fill(tx, iy + 20, tx + barW, iy + 25, 0xFF2A0606);
        g.fillGradient(tx, iy + 20, tx + Math.round(barW * blood), iy + 25, 0xFFE02020, 0xFF7A0808);
        g.drawString(font, Component.translatable("hud.csm.blood", (int) data.blood()), tx, iy + 28, 0xFFD83030, true);

        // selected ability
        int sel = Math.min(data.selected(), abilities.size() - 1);
        Ability ab = abilities.get(sel);
        g.fill(ix - 1, iy - 1, ix + 25, iy + 25, data.isTransformed() ? 0xFF000000 | data.type().color : 0xFF444444);
        g.fill(ix, iy, ix + 24, iy + 24, 0xFF140404);
        g.blit(ab.icon(), ix, iy, 24, 24, 0, 0, 32, 32, 32, 32);
        int cd = data.cooldown(sel);
        if (cd > 0) {
            int h = Math.round(24f * cd / Math.max(1, data.cooldownMax(sel)));
            g.fill(ix, iy + 24 - h, ix + 24, iy + 24, 0xA0000000);
        }
        Component name = ab.isTrigger() && data.isTransformed() ? Component.translatable("ability.csm.revert") : ab.displayName();
        g.drawString(font, name.copy().withStyle(ChatFormatting.BOLD), tx, iy, 0xFFFFFFFF, true);
        g.drawString(font, Component.translatable("hud.csm.keys", Keybinds.USE.getTranslatedKeyMessage(),
                Keybinds.WHEEL.getTranslatedKeyMessage()), tx, iy + 9, 0xFF9A9A9A, true);
    }

    private HybridHud() {
    }
}
