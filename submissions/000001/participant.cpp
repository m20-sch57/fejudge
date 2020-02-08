import kotlin.math.absoluteValue
import kotlin.math.max

interface Ring<T> {
    fun add(a : )
    fun zero() : R
}

class Polynom<T : > (var ai: List<T>) {
//    constructor() : this(listOf(T()!!.zero)) ?? How make 0?
    constructor(x: T) : this(listOf(x))

    override fun toString() : String {
        return this.ai.withIndex().reversed().joinToString(
            "+", transform = { (idx : Int, coef: T) -> coef.toString() + "x^$idx" })
    }

    fun degree() : Int {
        return this.ai.size
    }

    operator fun plus(other : Polynom<T>) : Polynom<T> {
        this.ai[0] + this.ai[0]
        return this
    }
}

abstract class Pair<T> (var _x: T, var _y: T) {
    abstract fun sum() : T
    abstract fun product() : T
    abstract fun gcd() : T

    fun swap() {
        val c = this._x
        this._x = this._y
        this._y = c
    }
}

class IntPair (var x: Int, var y: Int) : Pair<Int>(x, y) {
    constructor() : this(0, 0)
    constructor(x: Int) : this(x, 0)
    constructor(arr: List<Int>) : this(
        arr.getOrElse(0, { 0 }),
        arr.getOrElse(1, { 0 })
    )

    override fun sum() : Int {
        return this.x + this.y
    }

    override fun product() : Int {
        return this.x * this.y
    }

    override fun gcd() : Int {
        if (this.product() == 0) return this.sum().absoluteValue
        return IntPair(this.y % this.x, this.x).gcd()
    }

}
fun testIntPair() {
    while (true) {
        val point = IntPair(
            readLine()!!.toInt(),
            readLine()!!.toInt()
        )
        println(point.gcd())
    }
}

fun testOperatorOverride() {
    println(Polynom<Int>(listOf(5, 10)) + Polynom<Int>(listOf(5, 7)))
}

fun main()
{
    testOperatorOverride()
}