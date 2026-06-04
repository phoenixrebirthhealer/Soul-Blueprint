<?php
// Phoenix Rebirth | Hebrew Metatron's Cube Frequency System
// Proprietary — Christina Stevens
// Hebrew letter values are COMPLETELY SEPARATE from numerology values. Never mix them.

function _heb_single() {
    return array(
        'A'=>1,  'B'=>2,  'C'=>11, 'D'=>4,  'E'=>5,  'F'=>17, 'G'=>3,  'H'=>5,
        'I'=>10, 'J'=>10, 'K'=>19, 'L'=>12, 'M'=>13, 'N'=>14, 'O'=>6,  'P'=>17,
        'Q'=>19, 'R'=>20, 'S'=>15, 'T'=>9,  'U'=>6,  'V'=>6,  'W'=>6,  'X'=>15,
        'Y'=>16, 'Z'=>7,
    );
}

function _heb_combo() {
    return array(
        'AH'=>5, 'CH'=>8, 'WH'=>16, 'TZ'=>18, 'SH'=>21, 'TA'=>22, 'TH'=>22,
    );
}

function _heb_final() {
    return array('M'=>12, 'P'=>12);
}

function _heb_fibonacci() {
    return array(1, 2, 3, 5, 8, 13, 21);
}

function _heb_element_map() {
    return array(
        'Void'  => array(0),
        'Fire'  => array(3, 10, 11, 15, 21),
        'Water' => array(8, 13, 14, 18),
        'Earth' => array(2, 4, 6, 9, 16, 19, 22),
        'Air'   => array(1, 5, 7, 12, 17, 20),
    );
}

function _heb_letter_ref() {
    return array(
        0  => array('name' => 'The Fool', 'element' => 'Void',  'meaning' => 'Pure potential. Anticipation. The soul that has leaped before and KNOWS. The center from which all journeys begin.'),
        1  => array('name' => 'Aleph',   'element' => 'Air',   'meaning' => 'The silent breath. The threshold. The void before sound.'),
        2  => array('name' => 'Bet',     'element' => 'Earth', 'meaning' => 'The sacred container. The house that holds what is created.'),
        3  => array('name' => 'Gimel',   'element' => 'Fire',  'meaning' => 'The camel. Bridge between worlds. Movement across wilderness.'),
        4  => array('name' => 'Dalet',   'element' => 'Earth', 'meaning' => 'The door. The threshold. The passage between what was and what is.'),
        5  => array('name' => 'Heh',     'element' => 'Air',   'meaning' => 'The divine breath. The window of revelation. Presence.'),
        6  => array('name' => 'Vav',     'element' => 'Earth', 'meaning' => 'The nail. The connector between heaven and earth.'),
        7  => array('name' => 'Zayin',   'element' => 'Air',   'meaning' => 'The sword of discernment. Divinity as protection.'),
        8  => array('name' => 'Chet',    'element' => 'Water', 'meaning' => 'CHAI. Life itself. The sacred container where life grows.'),
        9  => array('name' => 'Tet',     'element' => 'Earth', 'meaning' => 'The serpent. The hidden goodness coiled and waiting to rise.'),
        10 => array('name' => 'Yod',     'element' => 'Fire',  'meaning' => 'The divine spark. Smallest letter containing greatest power.'),
        11 => array('name' => 'Kaf',     'element' => 'Fire',  'meaning' => 'The open palm. Power received and held.'),
        12 => array('name' => 'Lamed',   'element' => 'Air',   'meaning' => 'The teacher reaching toward heaven.'),
        13 => array('name' => 'Mem',     'element' => 'Water', 'meaning' => 'The primordial waters. The unconscious depths.'),
        14 => array('name' => 'Nun',     'element' => 'Water', 'meaning' => 'The fish. Faithful movement through the deep.'),
        15 => array('name' => 'Samech',  'element' => 'Fire',  'meaning' => 'The perfect circle. Divine support. Grace.'),
        16 => array('name' => 'Ayin',    'element' => 'Earth', 'meaning' => 'The eye. The spring. Clear seeing beyond the physical.'),
        17 => array('name' => 'Peh',     'element' => 'Air',   'meaning' => 'The mouth. The voice. The breath of authentic expression.'),
        18 => array('name' => 'Tzadi',   'element' => 'Water', 'meaning' => 'The fish hook. The tzaddik. Pulling wisdom from the deep.'),
        19 => array('name' => 'Qof',     'element' => 'Earth', 'meaning' => 'The horizon. The cycle that always returns.'),
        20 => array('name' => 'Resh',    'element' => 'Air',   'meaning' => 'The head. The beginning. The face turned toward what is next.'),
        21 => array('name' => 'Shin',    'element' => 'Fire',  'meaning' => 'The divine fire. Love. The letter with which God signed creation.'),
        22 => array('name' => 'Tav',     'element' => 'Earth', 'meaning' => 'The seal. The divine signature. The completion.'),
    );
}

function hebrew_get_element($pos) {
    foreach (_heb_element_map() as $element => $positions) {
        if (in_array($pos, $positions, true)) return $element;
    }
    return null;
}

function hebrew_apply_overflow($n) {
    if ($n <= 22) return array('position' => $n, 'is_bridge' => false);
    if ($n % 9 === 0) return array('position' => (int)($n / 9), 'is_bridge' => false);
    $result = $n / 9;
    return array(
        'position'  => $n,
        'bridge'    => array((int)floor($result), (int)ceil($result)),
        'is_bridge' => true,
    );
}

function hebrew_parse_name($name, $is_final_name = false) {
    $single = _heb_single();
    $combo  = _heb_combo();
    $final  = _heb_final();
    $upper  = strtoupper(preg_replace('/[^A-Za-z]/', '', $name));
    $units  = array();
    $i      = 0;
    $len    = strlen($upper);
    while ($i < $len) {
        $two = substr($upper, $i, 2);
        if (strlen($two) === 2 && isset($combo[$two])) {
            $units[] = array('letters' => $two, 'value' => $combo[$two], 'is_combo' => true, 'is_final_letter' => false);
            $i += 2;
        } else {
            $ch      = $upper[$i];
            $is_last = $is_final_name && ($i === $len - 1);
            $value   = ($is_last && isset($final[$ch])) ? $final[$ch] : (isset($single[$ch]) ? $single[$ch] : 0);
            $units[] = array('letters' => $ch, 'value' => $value, 'is_combo' => false, 'is_final_letter' => $is_last);
            $i++;
        }
    }
    return $units;
}

function hebrew_calc_layer1($first, $middle, $last) {
    $names = array();
    foreach (array($first, $middle, $last) as $n) {
        if (strlen(trim($n)) > 0) $names[] = $n;
    }
    $activations = array();
    $name_count  = count($names);
    foreach ($names as $name_idx => $name) {
        $is_final = ($name_idx === $name_count - 1);
        $units    = hebrew_parse_name($name, $is_final);
        foreach ($units as $pos_idx => $unit) {
            $position  = $pos_idx + 1;
            $sum       = $unit['value'] + $position;
            $overflow  = hebrew_apply_overflow($sum);
            $activations[] = array_merge(array(
                'name'            => $name,
                'letters'         => $unit['letters'],
                'letter_value'    => $unit['value'],
                'position'        => $position,
                'sum'             => $sum,
                'is_combo'        => $unit['is_combo'],
                'is_final_letter' => $unit['is_final_letter'],
            ), $overflow);
        }
    }
    return $activations;
}

function hebrew_calc_layer2($day, $month, $year) {
    $digits   = str_split((string)$year);
    $year_sum = 0;
    foreach ($digits as $d) $year_sum += (int)$d;
    return array(
        array_merge(array('unit' => 'Day',   'raw' => (int)$day),      hebrew_apply_overflow((int)$day)),
        array_merge(array('unit' => 'Month', 'raw' => (int)$month),    hebrew_apply_overflow((int)$month)),
        array_merge(array('unit' => 'Year',  'raw' => $year_sum),      hebrew_apply_overflow($year_sum)),
    );
}

function run_hebrew_calculation($first, $middle, $last, $day, $month, $year) {
    $letter_ref  = _heb_letter_ref();
    $fibonacci   = _heb_fibonacci();

    $layer1 = hebrew_calc_layer1($first, $middle, $last);
    $layer2 = hebrew_calc_layer2($day, $month, $year);

    $l1_pos = array();
    foreach ($layer1 as $a) {
        if (!$a['is_bridge'] && $a['position'] <= 22) $l1_pos[] = $a['position'];
    }
    $l2_pos = array();
    foreach ($layer2 as $a) {
        if (!$a['is_bridge'] && $a['position'] <= 22) $l2_pos[] = $a['position'];
    }
    $all_pos = array_merge($l1_pos, $l2_pos);

    $convergence = array_values(array_intersect($l1_pos, $l2_pos));

    $element_counts = array('Fire' => 0, 'Water' => 0, 'Earth' => 0, 'Air' => 0);
    foreach ($all_pos as $pos) {
        $el = hebrew_get_element($pos);
        if ($el && $el !== 'Void' && isset($element_counts[$el])) $element_counts[$el]++;
    }

    $elemental_wounds = array();
    foreach ($element_counts as $el => $cnt) {
        if ($cnt === 0) $elemental_wounds[] = $el;
    }

    $dominant_element = null;
    $max_count = -1;
    foreach ($element_counts as $el => $cnt) {
        if ($cnt > $max_count) { $max_count = $cnt; $dominant_element = $el; }
    }

    $activation_count = array();
    foreach ($all_pos as $pos) {
        $activation_count[$pos] = isset($activation_count[$pos]) ? $activation_count[$pos] + 1 : 1;
    }

    $enrich = function($positions) use ($activation_count, $letter_ref, $fibonacci) {
        $result = array();
        foreach ($positions as $pos) {
            $ref = isset($letter_ref[$pos]) ? $letter_ref[$pos] : array();
            $result[] = array_merge($ref, array(
                'position'         => $pos,
                'is_fibonacci'     => in_array($pos, $fibonacci, true),
                'element'          => hebrew_get_element($pos),
                'activation_count' => isset($activation_count[$pos]) ? $activation_count[$pos] : 1,
            ));
        }
        return $result;
    };

    $fibonacci_activations = array();
    foreach ($all_pos as $p) {
        if (in_array($p, $fibonacci, true)) $fibonacci_activations[] = $p;
    }

    return array(
        'first_name'            => $first,
        'middle_name'           => $middle,
        'last_name'             => $last,
        'date_of_birth'         => array('day' => $day, 'month' => $month, 'year' => $year),
        'layer1'                => $layer1,
        'layer2'                => $layer2,
        'convergence_points'    => $convergence,
        'convergence_details'   => $enrich($convergence),
        'layer1_positions'      => $enrich($l1_pos),
        'layer2_positions'      => $enrich($l2_pos),
        'element_counts'        => $element_counts,
        'elemental_wounds'      => array_values($elemental_wounds),
        'dominant_element'      => $dominant_element,
        'fibonacci_activations' => $fibonacci_activations,
        'activation_count'      => $activation_count,
    );
}
