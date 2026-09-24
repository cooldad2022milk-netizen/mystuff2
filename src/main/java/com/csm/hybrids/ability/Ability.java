package com.csm.hybrids.ability;

import com.csm.hybrids.CsmMod;
import com.csm.hybrids.hybrid.HybridData;
import com.csm.hybrids.hybrid.HybridType;
import com.csm.hybrids.network.AnimSpec;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;

/**
 * One move on a hybrid's ability wheel.
 * <p>
 * Server flow: {@link #checkUse} -> {@link #prepare} -> {@link #start} -> {@link #tick} (every tick,
 * {@code run.tick} counts from 0) -> {@link #end}. The {@link AnimSpec} built in {@link #prepare} is sent to
 * every client watching the player so the body (PlayerAnimator) and devil parts (GeckoLib) animate in sync.
 */
public abstract class Ability {
    public final HybridType type;
    public final String id;
    protected int duration = 20;
    protected int cooldown = 20;
    protected float bloodCost;
    protected boolean requiresForm = true;
    protected String playerAnim = "";
    protected String geoAnim = "";
    protected String geoController = "action";
    protected String fx = "";
    protected boolean revs;

    protected Ability(HybridType type, String id) {
        this.type = type;
        this.id = id;
    }

    // -------------------------------------------------------------- builder helpers
    protected Ability timing(int duration, int cooldown) {
        this.duration = duration;
        this.cooldown = cooldown;
        return this;
    }

    protected Ability cost(float blood) {
        this.bloodCost = blood;
        return this;
    }

    protected Ability anim(String playerAnim, String geoAnim) {
        this.playerAnim = playerAnim;
        this.geoAnim = geoAnim;
        return this;
    }

    protected Ability fx(String fx) {
        this.fx = fx;
        return this;
    }

    protected Ability revs() {
        this.revs = true;
        return this;
    }

    protected Ability anyForm() {
        this.requiresForm = false;
        return this;
    }

    // -------------------------------------------------------------- metadata (both sides)
    public int cooldown() {
        return cooldown;
    }

    public int duration() {
        return duration;
    }

    public float bloodCost() {
        return bloodCost;
    }

    public boolean requiresForm() {
        return requiresForm;
    }

    public boolean isTrigger() {
        return false;
    }

    public String playerAnim() {
        return playerAnim;
    }

    public String geoAnim() {
        return geoAnim;
    }

    public String fxGroup() {
        return fx;
    }

    public Component displayName() {
        return Component.translatable("ability.csm." + id);
    }

    public Component description() {
        return Component.translatable("ability.csm." + id + ".desc");
    }

    public ResourceLocation icon() {
        return CsmMod.id("textures/gui/ability/" + id + ".png");
    }

    /** What the move costs besides blood (a contract's price), shown on the wheel; null for none. */
    public Component price() {
        return null;
    }

    /** Colour of this move's slice on the wheel. */
    public int wheelColor() {
        return type.color;
    }

    public boolean consumesBloodOnStart() {
        return true;
    }

    // -------------------------------------------------------------- server
    /** @return null when usable, otherwise a translation key explaining why not. */
    public String checkUse(ServerPlayer player, HybridData data) {
        if (requiresForm && !data.isTransformed()) {
            return "msg.csm.need_form";
        }
        if (data.blood() < bloodCost) {
            return "msg.csm.no_blood";
        }
        return null;
    }

    public void prepare(ServerPlayer player, HybridData data, AbilityRun run) {
        run.duration = duration;
        run.anim = new AnimSpec(playerAnim, geoController, geoAnim, fx, revs, AnimSpec.ABILITY, duration);
    }

    public void start(ServerPlayer player, HybridData data, AbilityRun run) {
    }

    public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
    }

    public void end(ServerPlayer player, HybridData data, AbilityRun run) {
    }
}
