#pragma once

namespace duke {
/**
 * The class hazard does things
 */
class hazard {
private:
		/**
		 * This is some value
		 */
		int some_value;
public:
		/**
		 * The default constructor
		 */
		hazard() = default;
};

/**
 * This is an example of a class being specialized
 */
template <typename T>
class bruh;

/**
 * Bruh in specialised
 */
template<>
class bruh<char> {
private:
		/**
		 * This is a hazard class member of bruh
		 */
		hazard haz_;
public:
		/**
		 * Something you should never do
		 */
		void eat_poop(){}

		/**
		 * Something you should do
		 */
		float touch_grass( int x) const {
				(void) x;
				return 5.f;
		}

		/**
		 * Return const reference of hazard member
		 */
		const hazard& get_haze() const {
				return haz_;
		}
};

/**
 * Global function inside a namespace
 */
void chicken();
}
