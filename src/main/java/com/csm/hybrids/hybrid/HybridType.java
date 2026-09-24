package com.csm.hybrids.hybrid;

import com.csm.hybrids.ability.Abilities;
import com.csm.hybrids.ability.Ability;
import net.minecraft.network.chat.Component;

import java.util.List;
import java.util.Locale;

/**
 * The devil living in the player.
 * <p>
 * <b>Hybrids</b> have a devil's heart beating in their chest and use a manga trigger to let the devil burst out:
 * <ul>
 *   <li>CHAINSAW - yank the starter cord out of the chest (transforms on the yank)</li>
 *   <li>CROSSBOW - draw the arrow out of the right eye socket (transforms once it's out)</li>
 *   <li>FLAMETHROWER - bite down on the trigger molar (transforms on the click)</li>
 *   <li>WHIP - snap the fingers to mimic a whipcrack</li>
 *   <li>BOMB - pull the grenade pin in the neck (under the choker)</li>
 *   <li>SPEAR - pull a spear out of the nape</li>
 *   <li>KATANA - pull off the left hand; a katana rises out of the stump</li>
 *   <li>LONGSWORD - pull off the right hand, baring the blade inside the arm</li>
 * </ul>
 * <b>Fiends</b> are devils wearing a corpse: the player dies and the devil takes the body over. Their devil
 * features (horns, shark head, mask, exposed brain, gun barrel) are always showing; slot 0 is not a trigger but
 * the fiend unleashing more of its devil nature (Galgali removing his mask, Beam's shark skull...).
 * <p>
 * Timings (ticks) are shared by the server logic and the client animations.
 */
public enum HybridType {
    NONE("none", 0x9A9A9A, 0, 0, 0, 0, false, "none"),
    CHAINSAW("chainsaw", 0xF0782A, 24, 12, 12, 7, false, "chainsaw"),
    CROSSBOW("crossbow", 0xC9CED8, 30, 20, 12, 7, true, "crossbow"),
    FLAMETHROWER("flamethrower", 0xE24A1E, 20, 9, 12, 7, true, "flame"),
    /** Snaps her fingers like a whipcrack; the hands burst into whips. */
    WHIP("whip", 0xE0604A, 16, 8, 12, 7, false, "whip"),
    /** Hooks the grenade pin hidden under her choker and yanks it - she detonates into the bomb form. */
    BOMB("bomb", 0x5A5A68, 22, 12, 12, 7, false, "bomb"),
    /** Draws a spear out of the nape of his neck. */
    SPEAR("spear", 0x9A6A52, 26, 18, 12, 7, true, "spear"),
    /** Katana Man: pulls off his left hand and a katana rises out of the stump. */
    KATANA("katana", 0xC4C8D2, 24, 12, 16, 10, false, "katana"),
    /** Sword Man (Longsword): pulls off his right hand, baring the blade hidden inside the arm. */
    LONGSWORD("longsword", 0x8A90A8, 24, 12, 14, 8, false, "longsword"),

    /** Power: horns grow and multiply as she gorges on blood. */
    BLOOD("blood", 0xC0182A, 20, 10, 12, 7, false, "blood", true, false, false),
    /** Beam: shark head always; his devil side swells it into a giant six-eyed shark skull. */
    SHARK("shark", 0x6F8FA8, 18, 9, 12, 7, false, "shark", true, true, true),
    /** Galgali: the plague-doctor mask keeps him weak; take it off and he becomes huge. */
    VIOLENCE("violence", 0x46A84E, 24, 12, 16, 10, false, "violence", true, false, true),
    /** Cosmo: exposed brain, heart pupils, "Halloween". */
    COSMOS("cosmos", 0xF08CC8, 20, 10, 12, 7, false, "cosmos", true, false, false),
    /** The Gun Devil wearing Aki: pistol barrel through the face, a rifle for a forearm. */
    GUN("gun", 0x5A5E66, 20, 10, 12, 7, false, "gun", true, false, false),

    // ------------------------------------------------------------------ full devils (fought as mobs, their essence
    // makes you one). Humanoid devils keep a human body; the rest manifest as their true form (slot 0).
    /** Makima, the Control Devil. */
    CONTROL("control", 0xB8322A, true),
    BAT("bat", 0x7A5A8A, false),
    LEECH("leech", 0x7A4A56, false),
    ZOMBIE("zombie", 0x7A8A5A, false),
    TOMATO("tomato", 0xD83A2A, false),
    SEA_CUCUMBER("sea_cucumber", 0xA07A62, false),
    ETERNITY("eternity", 0xC89A8A, false),
    DARKNESS("darkness", 0x5A5A70, false),
    /** The Gun Devil itself (the Gun Fiend is a fragment of it wearing Aki). */
    GUN_DEVIL("gun_devil", 0x8A8E96, false),
    TYPHOON("typhoon", 0x9AB0C8, false),
    // the devils Public Safety makes contracts with: fought as mobs, never become (see contract.Contract)
    FOX("fox", 0xF4F0E6, false, true),
    CURSE("curse", 0xD8D0B8, false, true),
    FUTURE("future", 0xC8A870, false, true),
    GHOST("ghost", 0xE8E0F0, false, true),
    ANGEL("angel", 0xF0E0B0, true),
    /** Yoru, the War Devil. */
    WAR("war", 0xB02828, true),
    /** Fami, the Famine Devil. */
    FAMINE("famine", 0xE890B0, true),
    FALLING("falling", 0xF0F0F0, false),
    JUSTICE("justice", 0x8A9A5A, false),
    /**
     * The Chainsaw Devil's true form - Pochita as the Hero of Hell. It is fought as a mob, but no player eats its
     * essence: it only ever comes out of a Chainsaw hybrid, taking Denji over for a while (see {@link #host()}).
     */
    CHAINSAW_DEVIL("chainsaw_devil", 0x2A2A30, false),
    /** Princi, the Spider Devil: a woman from the waist up with a zipper down her face, eight knife-legs below. */
    SPIDER("spider", 0x3A2A36, false),
    /** The Aging Devil, a Primal Devil from part 2. */
    AGING("aging", 0xB8A890, false);

    public final String id;
    public final int color;
    /** Total length of the transformation trigger animation. */
    public final int triggerTicks;
    /** Tick of the trigger animation on which the devil form bursts out. */
    public final int transformAt;
    public final int revertTicks;
    public final int revertAt;
    /** Whether the devil form replaces the vanilla arms entirely (crossbow arms, flamethrower arms). */
    public final boolean replacesArms;
    /** Prefix used for this hybrid's PlayerAnimator animation ids. */
    public final String animPrefix;
    /** A devil possessing a corpse instead of a devil's heart in a living chest. */
    public final boolean fiend;
    /** Hide the vanilla head even outside the devil form (Beam's head is a shark's). */
    public final boolean baseHidesHead;
    /** Hide the vanilla head while the devil form is out. */
    public final boolean formHidesHead;
    /** A full devil (not a hybrid or a fiend): a mob you can fight, and a form you can take by eating its essence. */
    public final boolean devil;
    /** A devil in human shape (Makima, Angel, Yoru, Fami): its parts are worn on the player like a fiend's. */
    public final boolean humanoid;
    /**
     * A devil people make contracts with (Fox, Curse, Future, Ghost). It is only ever a mob: players get its power
     * through a {@link com.csm.hybrids.contract.Contract}, never by becoming it.
     */
    public final boolean contract;

    HybridType(String id, int color, int triggerTicks, int transformAt, int revertTicks, int revertAt,
               boolean replacesArms, String animPrefix) {
        this(id, color, triggerTicks, transformAt, revertTicks, revertAt, replacesArms, animPrefix, false, false, true);
    }

    HybridType(String id, int color, int triggerTicks, int transformAt, int revertTicks, int revertAt,
               boolean replacesArms, String animPrefix, boolean fiend, boolean baseHidesHead, boolean formHidesHead) {
        this.id = id;
        this.color = color;
        this.triggerTicks = triggerTicks;
        this.transformAt = transformAt;
        this.revertTicks = revertTicks;
        this.revertAt = revertAt;
        this.replacesArms = replacesArms;
        this.animPrefix = animPrefix;
        this.fiend = fiend;
        this.baseHidesHead = baseHidesHead;
        this.formHidesHead = formHidesHead;
        this.devil = false;
        this.humanoid = false;
        this.contract = false;
    }

    /** A full devil. Slot 0 manifests its true form (monsters) or lets the devil take over (humanoids). */
    HybridType(String id, int color, boolean humanoid) {
        this(id, color, humanoid, false);
    }

    HybridType(String id, int color, boolean humanoid, boolean contract) {
        this.id = id;
        this.color = color;
        this.triggerTicks = humanoid ? 20 : 24;
        this.transformAt = humanoid ? 10 : 12;
        this.revertTicks = humanoid ? 12 : 16;
        this.revertAt = humanoid ? 7 : 8;
        this.replacesArms = false;
        this.animPrefix = id;
        this.fiend = false;
        this.baseHidesHead = false;
        this.formHidesHead = false;
        this.devil = true;
        this.humanoid = humanoid;
        this.contract = contract;
    }

    /**
     * The hybrid whose devil this form is, for the forms that only come out of a hybrid and take it over for a while
     * (Pochita's true form out of Denji); NONE for everything else.
     */
    public HybridType host() {
        return this == CHAINSAW_DEVIL ? CHAINSAW : NONE;
    }

    /** A form a hybrid is taken over by, never a type of its own (see {@link #host()}). */
    public boolean takeover() {
        return host() != NONE;
    }

    /** Whether a player can be this for good (not the contract devils, not a takeover form). */
    public boolean playable() {
        return !contract && !takeover();
    }

    /** A devil whose form replaces the player's body with its own model. */
    public boolean monster() {
        return devil && !humanoid;
    }

    public List<Ability> abilities() {
        return Abilities.forType(this);
    }

    public Component displayName() {
        return Component.translatable("hybrid.csm." + id);
    }

    public static HybridType byId(String id) {
        for (HybridType t : values()) {
            if (t.id.equals(id.toLowerCase(Locale.ROOT))) {
                return t;
            }
        }
        return NONE;
    }

    public static HybridType byOrdinal(int ordinal) {
        HybridType[] v = values();
        return ordinal >= 0 && ordinal < v.length ? v[ordinal] : NONE;
    }
}
