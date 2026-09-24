package com.csm.hybrids.ability;

import com.csm.hybrids.network.AnimSpec;
import it.unimi.dsi.fastutil.ints.IntOpenHashSet;
import it.unimi.dsi.fastutil.ints.IntSet;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.phys.Vec3;

/** Server-side bookkeeping for one ability in progress. */
public class AbilityRun {
    public final Ability ability;
    public final int index;
    public int tick;
    public int duration;
    public AnimSpec anim;

    /** Trigger abilities: transform or revert. */
    public boolean reverting;
    public boolean failed;
    public Entity target;
    public Vec3 vec;
    public Vec3 vec2;
    public int counter;
    public final IntSet hit = new IntOpenHashSet();

    public AbilityRun(Ability ability, int index) {
        this.ability = ability;
        this.index = index;
    }
}
