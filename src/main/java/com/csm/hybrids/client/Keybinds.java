package com.csm.hybrids.client;

import com.mojang.blaze3d.platform.InputConstants;
import net.minecraft.client.KeyMapping;
import net.minecraftforge.client.settings.KeyConflictContext;
import org.lwjgl.glfw.GLFW;

public final class Keybinds {
    public static final String CATEGORY = "key.categories.csm";

    /** Hold to open the ability wheel, release to pick (tap to keep it open). */
    public static final KeyMapping WHEEL = new KeyMapping("key.csm.ability_wheel", KeyConflictContext.IN_GAME,
            InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_V, CATEGORY);
    /** Perform the ability selected on the wheel. */
    public static final KeyMapping USE = new KeyMapping("key.csm.use_ability", KeyConflictContext.IN_GAME,
            InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_R, CATEGORY);
    /** Shortcut for the trigger (pull cord / pull arrow / bite molar), wheel slot 1. */
    public static final KeyMapping TRIGGER = new KeyMapping("key.csm.trigger", KeyConflictContext.IN_GAME,
            InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_G, CATEGORY);

    private Keybinds() {
    }
}
