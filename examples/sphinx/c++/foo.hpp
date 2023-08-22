#pragma once

namespace duke {
class hazard {
private:
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

template<>
class bruh<char> {
private:
		hazard haz_;
public:

		void eat_poop(){}

		float touch_grass() const {
				return 5.f;
		}

		/**
		 * Return value
		 */
		const hazard& get_haze() const {
				return haz_;
		}
};


}
